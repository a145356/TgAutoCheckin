"""
Main entry point for Telegram Auto Check-In System.
Sets up scheduler and runs the application 24/7.
"""
import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
import pytz
from src.auth import TelegramAuth
from src.checkin import CheckInManager
from src.config import config
from src.utils.logger import logger


class CheckInBot:
    """Main application class for the check-in bot."""
    
    def __init__(self):
        """Initialize the bot."""
        self.auth = TelegramAuth()
        self.client = None
        self.checkin_manager = None
        self.scheduler = None
        self.timezone = pytz.timezone(config.TIMEZONE)
    
    async def initialize(self):
        """Initialize bot components."""
        logger.info("🤖 Initializing Telegram Check-In Bot...")
        logger.info(f"   Timezone: {config.TIMEZONE}")
        logger.info(f"   Groups: {len(config.GROUP_IDS)}")
        logger.info(f"   Keywords: {', '.join(config.KEYWORDS)}")
        logger.info("")
        
        # Initialize Telegram client
        self.client = await self.auth.initialize()
        
        # Initialize check-in manager
        self.checkin_manager = CheckInManager(self.client)
        
        # Initialize scheduler
        self.scheduler = AsyncIOScheduler(timezone=self.timezone)
        
        # Schedule daily check-in at 00:00
        self.scheduler.add_job(
            self.daily_checkin_job,
            trigger=CronTrigger(hour=0, minute=0, timezone=self.timezone),
            id='daily_checkin',
            name='Daily Check-In at 00:00',
            replace_existing=True
        )
        logger.info("✓ Scheduled daily check-in at 00:00 Singapore time")
        
        # Schedule hourly retry check
        self.scheduler.add_job(
            self.hourly_retry_job,
            trigger=IntervalTrigger(hours=1),
            id='hourly_retry',
            name='Hourly Retry Check',
            replace_existing=True
        )
        logger.info("✓ Scheduled hourly retry check")
        
        logger.info("")
        logger.info("=" * 60)
        logger.info("✅ BOT INITIALIZED SUCCESSFULLY")
        logger.info("=" * 60)
        logger.info("")
    
    async def daily_checkin_job(self):
        """Daily check-in job triggered at 00:00."""
        try:
            logger.info("⏰ Daily check-in job triggered!")
            
            # Reset daily state
            self.checkin_manager.reset_daily()
            
            # Execute check-in
            await self.checkin_manager.execute_checkin()
            
        except Exception as e:
            logger.error(f"✗ Error in daily check-in job: {e}", exc_info=True)
    
    async def hourly_retry_job(self):
        """Hourly retry job for failed check-ins."""
        try:
            # Check if there are pending groups
            if not self.checkin_manager.pending_groups:
                logger.debug("Hourly check: No pending check-ins")
                return
            
            logger.info("⏰ Hourly retry job triggered!")
            logger.info(f"   Pending groups: {len(self.checkin_manager.pending_groups)}")
            
            # Execute check-in
            await self.checkin_manager.execute_checkin()
            
        except Exception as e:
            logger.error(f"✗ Error in hourly retry job: {e}", exc_info=True)
    
    async def run(self):
        """Run the bot."""
        try:
            # Initialize
            await self.initialize()
            
            # Start scheduler
            self.scheduler.start()
            logger.info("🚀 Scheduler started")
            logger.info("   Waiting for scheduled tasks...")
            logger.info("")
            
            # Print next run times
            jobs = self.scheduler.get_jobs()
            for job in jobs:
                next_run = job.next_run_time
                logger.info(f"📅 {job.name}")
                logger.info(f"   Next run: {next_run.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            
            logger.info("")
            logger.info("=" * 60)
            logger.info("🟢 BOT IS RUNNING")
            logger.info("   Press Ctrl+C to stop")
            logger.info("=" * 60)
            logger.info("")
            
            # Keep the bot running
            while True:
                await asyncio.sleep(60)
        
        except KeyboardInterrupt:
            logger.info("\n⚠ Received shutdown signal...")
        
        except Exception as e:
            logger.error(f"✗ Fatal error: {e}", exc_info=True)
        
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Shutdown the bot gracefully."""
        logger.info("🛑 Shutting down bot...")
        
        if self.scheduler:
            self.scheduler.shutdown()
            logger.info("✓ Scheduler stopped")
        
        if self.auth:
            await self.auth.close()
        
        logger.info("✓ Shutdown complete")


async def main():
    """Main entry point."""
    try:
        # Print banner
        print("=" * 60)
        print("  Telegram Auto Check-In System")
        print("  Version 1.0.0")
        print("=" * 60)
        print()
        
        # Create and run bot
        bot = CheckInBot()
        await bot.run()
    
    except Exception as e:
        logger.error(f"✗ Failed to start bot: {e}", exc_info=True)
        raise


if __name__ == '__main__':
    # Run the bot
    asyncio.run(main())
