"""
Telegram authentication module using Telethon.
Handles UserBot login and session management.
"""
from telethon import TelegramClient
from telethon.sessions import StringSession
from src.config import config
from src.utils.logger import logger


class TelegramAuth:
    """Manages Telegram authentication and client lifecycle."""
    
    def __init__(self):
        """Initialize Telegram client."""
        self.client = None
    
    async def initialize(self) -> TelegramClient:
        """
        Initialize and authenticate Telegram client.
        
        Returns:
            Authenticated TelegramClient instance
        """
        logger.info("Initializing Telegram client...")
        
        # Create session directory if it doesn't exist
        session_path = config.get_session_path()
        
        # Create Telegram client
        self.client = TelegramClient(
            session_path,
            config.API_ID,
            config.API_HASH
        )
        
        # Start the client
        await self.client.start(phone=config.PHONE_NUMBER)
        
        # Check if we're authorized
        if await self.client.is_user_authorized():
            logger.info("✓ Successfully authenticated with Telegram")
            me = await self.client.get_me()
            logger.info(f"✓ Logged in as: {me.first_name} (@{me.username or 'no username'})")
        else:
            logger.error("✗ Authentication failed")
            raise RuntimeError("Failed to authenticate with Telegram")
        
        return self.client
    
    async def close(self):
        """Close the Telegram client connection."""
        if self.client:
            logger.info("Closing Telegram client...")
            await self.client.disconnect()
            logger.info("✓ Telegram client closed")
    
    def get_client(self) -> TelegramClient:
        """
        Get the current client instance.
        
        Returns:
            TelegramClient instance
        
        Raises:
            RuntimeError: If client is not initialized
        """
        if not self.client:
            raise RuntimeError("Client not initialized. Call initialize() first.")
        return self.client
