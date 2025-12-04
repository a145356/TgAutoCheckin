"""
Check-in execution module.
Sends check-in messages and manages retry logic.
"""
import asyncio
from typing import Dict, List
from datetime import datetime
from telethon import TelegramClient
from telethon.errors import FloodWaitError, ChatWriteForbiddenError
from src.config import config
from src.utils.logger import logger
from src.monitor import MessageMonitor


class CheckInManager:
    """Manages check-in execution and retry logic."""
    
    def __init__(self, client: TelegramClient):
        """
        Initialize check-in manager.
        
        Args:
            client: Authenticated TelegramClient instance
        """
        self.client = client
        self.monitor = MessageMonitor(client)
        self.retry_count = 0
        self.last_success: Dict[int, datetime] = {}
        self.pending_groups: List[int] = []
    
    async def execute_checkin(self) -> bool:
        """
        Execute check-in for all configured groups.
        
        Returns:
            True if all check-ins successful, False otherwise
        """
        logger.info("=" * 60)
        logger.info(f"🚀 Starting check-in process (Retry #{self.retry_count})")
        logger.info(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)
        
        # Get groups that need check-in
        groups_to_check = self.pending_groups if self.pending_groups else config.GROUP_IDS
        
        if not groups_to_check:
            logger.info("✓ All groups already checked in successfully")
            return True
        
        logger.info(f"📋 Groups to check-in: {len(groups_to_check)}")
        
        # Send check-in messages to all groups
        sent_groups = []
        for group_id in groups_to_check:
            try:
                logger.info(f"📤 Sending check-in to group {group_id}...")
                
                # Get group entity
                try:
                    entity = await self.client.get_entity(group_id)
                    logger.info(f"   Group: {getattr(entity, 'title', 'Unknown')}")
                except Exception as e:
                    logger.error(f"✗ Failed to get group entity: {e}")
                    continue
                
                # Send message
                await self.client.send_message(
                    entity,
                    config.CHECKIN_MESSAGE
                )
                logger.info(f"✓ Message sent: '{config.CHECKIN_MESSAGE}'")
                sent_groups.append(group_id)
                
                # Small delay to avoid flood
                await asyncio.sleep(2)
            
            except FloodWaitError as e:
                logger.warning(f"⚠ Flood wait error: need to wait {e.seconds} seconds")
                logger.info(f"   Waiting {e.seconds} seconds...")
                await asyncio.sleep(e.seconds)
                # Retry this group
                try:
                    await self.client.send_message(group_id, config.CHECKIN_MESSAGE)
                    sent_groups.append(group_id)
                except Exception as retry_error:
                    logger.error(f"✗ Retry failed: {retry_error}")
            
            except ChatWriteForbiddenError:
                logger.error(f"✗ Cannot write to group {group_id} (no permission)")
            
            except Exception as e:
                logger.error(f"✗ Failed to send message to group {group_id}: {e}")
        
        if not sent_groups:
            logger.error("✗ Failed to send check-in to any groups")
            return False
        
        # Monitor for success replies
        logger.info(f"\n📡 Monitoring {len(sent_groups)} groups for success replies...")
        success = await self.monitor.monitor_replies(sent_groups)
        
        if success:
            logger.info("=" * 60)
            logger.info("✅ CHECK-IN SUCCESSFUL!")
            logger.info(f"   Keywords detected: {', '.join(self.monitor.detected_keywords)}")
            logger.info("=" * 60)
            
            # Mark all groups as successful
            for group_id in sent_groups:
                self.last_success[group_id] = datetime.now()
            
            # Clear pending groups
            self.pending_groups.clear()
            self.retry_count = 0
            return True
        else:
            logger.warning("=" * 60)
            logger.warning("⚠ CHECK-IN STATUS UNKNOWN")
            logger.warning("   No success keywords detected in replies")
            logger.warning("   Will retry in 1 hour...")
            logger.warning("=" * 60)
            
            # Update pending groups
            self.pending_groups = sent_groups
            self.retry_count += 1
            return False
    
    def reset_daily(self):
        """Reset check-in state for new day."""
        logger.info("🔄 Resetting daily check-in state...")
        self.pending_groups = config.GROUP_IDS.copy()
        self.retry_count = 0
        self.last_success.clear()
        logger.info("✓ Daily state reset complete")
    
    def get_status(self) -> Dict:
        """
        Get current check-in status.
        
        Returns:
            Dictionary with status information
        """
        return {
            'retry_count': self.retry_count,
            'pending_groups': len(self.pending_groups),
            'successful_groups': len(self.last_success),
            'last_success_times': {
                gid: dt.strftime('%Y-%m-%d %H:%M:%S')
                for gid, dt in self.last_success.items()
            }
        }
