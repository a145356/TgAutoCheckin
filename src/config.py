"""
Configuration loader for Telegram Auto Check-In System.
Reads and validates environment variables from .env file.
"""
import os
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration manager for the application."""
    
    # Telegram API credentials
    API_ID: int = int(os.getenv('API_ID', '0'))
    API_HASH: str = os.getenv('API_HASH', '')
    PHONE_NUMBER: str = os.getenv('PHONE_NUMBER', '')
    
    # Check-in settings
    GROUP_IDS: List[int] = []
    CHECKIN_MESSAGE: str = os.getenv('CHECKIN_MESSAGE', '签到')
    TIMEZONE: str = os.getenv('TIMEZONE', 'Asia/Singapore')
    KEYWORDS: List[str] = []
    
    # Session settings
    SESSION_NAME: str = 'telegram_checkin'
    SESSION_DIR: str = 'session'
    
    # Monitoring settings
    MONITOR_TIMEOUT: int = 180  # 3 minutes in seconds
    
    def __init__(self):
        """Initialize and validate configuration."""
        self._load_group_ids()
        self._load_keywords()
        self._validate()
    
    def _load_group_ids(self):
        """Parse comma-separated group IDs from environment."""
        group_ids_str = os.getenv('GROUP_IDS', '')
        if group_ids_str:
            try:
                self.GROUP_IDS = [int(gid.strip()) for gid in group_ids_str.split(',')]
            except ValueError as e:
                raise ValueError(f"Invalid GROUP_IDS format: {e}")
    
    def _load_keywords(self):
        """Parse comma-separated keywords from environment."""
        keywords_str = os.getenv('KEYWORDS', '签到,成功,积分,获得')
        if keywords_str:
            self.KEYWORDS = [kw.strip() for kw in keywords_str.split(',')]
    
    def _validate(self):
        """Validate that all required settings are present."""
        errors = []
        
        if not self.API_ID or self.API_ID == 0:
            errors.append("API_ID is required. Get it from https://my.telegram.org/apps")
        
        if not self.API_HASH:
            errors.append("API_HASH is required. Get it from https://my.telegram.org/apps")
        
        if not self.PHONE_NUMBER:
            errors.append("PHONE_NUMBER is required (format: +1234567890)")
        
        if not self.GROUP_IDS:
            errors.append("GROUP_IDS is required. Use list_groups.py to find group IDs")
        
        if not self.KEYWORDS:
            errors.append("KEYWORDS is required for success detection")
        
        if errors:
            error_msg = "\n".join(f"  - {error}" for error in errors)
            raise ValueError(f"Configuration validation failed:\n{error_msg}")
    
    def get_session_path(self) -> str:
        """Get the full path to the session file."""
        os.makedirs(self.SESSION_DIR, exist_ok=True)
        return os.path.join(self.SESSION_DIR, self.SESSION_NAME)


# Global configuration instance
config = Config()
