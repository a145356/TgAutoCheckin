"""
Message monitoring module for detecting check-in success.
Listens for reply messages and detects success keywords.
"""
import asyncio
from typing import List, Set
from telethon import TelegramClient, events
from telethon.tl.types import Message
from src.config import config
from src.utils.logger import logger


class MessageMonitor:
    """Monitors incoming messages for success detection."""
    
    def __init__(self, client: TelegramClient):
        """
        Initialize message monitor.
        
        Args:
            client: Authenticated TelegramClient instance
        """
        self.client = client
        self.detected_keywords: Set[str] = set()
        self.success_detected = False
        self.monitoring = False
    
    async def monitor_replies(self, group_ids: List[int], timeout: int = None) -> bool:
        """
        Monitor messages in specified groups for success keywords.
        
        Args:
            group_ids: List of group IDs to monitor
            timeout: Timeout in seconds (default: from config)
        
        Returns:
            True if success keyword detected, False otherwise
        """
        if timeout is None:
            timeout = config.MONITOR_TIMEOUT
        
        logger.info(f"📡 Monitoring messages for {timeout} seconds...")
        logger.info(f"   Looking for keywords: {', '.join(config.KEYWORDS)}")
        
        # Reset state
        self.detected_keywords.clear()
        self.success_detected = False
        self.monitoring = True
        
        # Event handler for new messages
        @self.client.on(events.NewMessage(chats=group_ids))
        async def handler(event: events.NewMessage.Event):
            if not self.monitoring:
                return
            
            message: Message = event.message
            text = message.message or ""
            
            # Check if any keyword is in the message
            for keyword in config.KEYWORDS:
                if keyword in text:
                    self.detected_keywords.add(keyword)
                    self.success_detected = True
                    logger.info(f"✓ Success keyword detected: '{keyword}'")
                    logger.info(f"   Message: {text[:100]}...")
                    break
        
        try:
            # Wait for timeout or success
            start_time = asyncio.get_event_loop().time()
            while self.monitoring:
                elapsed = asyncio.get_event_loop().time() - start_time
                
                if elapsed >= timeout:
                    logger.info("⏱ Monitoring timeout reached")
                    break
                
                if self.success_detected:
                    logger.info("✓ Success detected, stopping monitor")
                    break
                
                # Sleep briefly to avoid busy waiting
                await asyncio.sleep(1)
        
        finally:
            # Stop monitoring
            self.monitoring = False
            # Remove the event handler
            self.client.remove_event_handler(handler)
        
        return self.success_detected
    
    def stop(self):
        """Stop monitoring."""
        self.monitoring = False
