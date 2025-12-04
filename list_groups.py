"""
Group Discovery Script
Lists all Telegram groups/channels the user has joined with their IDs.
Run this script to find group IDs for configuration.
"""
import asyncio
from telethon import TelegramClient
from telethon.tl.types import Channel, Chat
from src.config import config
from src.utils.logger import logger


async def list_groups():
    """List all groups and channels the user has joined."""
    print("=" * 70)
    print("  Telegram Group Discovery")
    print("=" * 70)
    print()
    
    # Create session path
    session_path = config.get_session_path()
    
    # Create client
    client = TelegramClient(
        session_path,
        config.API_ID,
        config.API_HASH
    )
    
    try:
        # Connect and authenticate
        print("🔐 Connecting to Telegram...")
        await client.start(phone=config.PHONE_NUMBER)
        
        if not await client.is_user_authorized():
            print("✗ Not authorized. Please run the main application first to log in.")
            return
        
        me = await client.get_me()
        print(f"✓ Logged in as: {me.first_name} (@{me.username or 'no username'})")
        print()
        
        # Get all dialogs (conversations)
        print("📋 Fetching groups and channels...")
        print()
        
        dialogs = await client.get_dialogs()
        
        groups = []
        channels = []
        
        for dialog in dialogs:
            entity = dialog.entity
            
            # Check if it's a group or channel
            if isinstance(entity, (Channel, Chat)):
                info = {
                    'title': dialog.title,
                    'id': entity.id,
                    'type': 'Channel' if isinstance(entity, Channel) and entity.broadcast else 'Group'
                }
                
                if isinstance(entity, Channel) and entity.broadcast:
                    channels.append(info)
                else:
                    groups.append(info)
        
        # Print groups
        if groups:
            print("=" * 70)
            print(f"📱 GROUPS ({len(groups)} found)")
            print("=" * 70)
            print()
            
            for i, group in enumerate(groups, 1):
                print(f"{i}. {group['title']}")
                print(f"   ID: {group['id']}")
                print(f"   Type: {group['type']}")
                print()
        else:
            print("No groups found.")
            print()
        
        # Print channels
        if channels:
            print("=" * 70)
            print(f"📢 CHANNELS ({len(channels)} found)")
            print("=" * 70)
            print()
            
            for i, channel in enumerate(channels, 1):
                print(f"{i}. {channel['title']}")
                print(f"   ID: {channel['id']}")
                print(f"   Type: {channel['type']}")
                print()
        else:
            print("No channels found.")
            print()
        
        # Print instructions
        print("=" * 70)
        print("ℹ️  INSTRUCTIONS")
        print("=" * 70)
        print()
        print("To use these groups in auto check-in:")
        print("1. Copy the ID(s) of the group(s) you want to check-in")
        print("2. Add them to your .env file as GROUP_IDS")
        print("3. Format: GROUP_IDS=-1001234567890,-1009876543210")
        print()
        print("Example .env entry:")
        print(f"GROUP_IDS={groups[0]['id']}" if groups else "GROUP_IDS=-1001234567890")
        print()
    
    except Exception as e:
        logger.error(f"✗ Error: {e}", exc_info=True)
        print(f"\n✗ Error: {e}")
        print("\nMake sure you have:")
        print("  1. Created a .env file with your API credentials")
        print("  2. Run the main application at least once to log in")
    
    finally:
        await client.disconnect()
        print("✓ Disconnected")


def main():
    """Main entry point."""
    try:
        asyncio.run(list_groups())
    except KeyboardInterrupt:
        print("\n⚠ Interrupted by user")
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")


if __name__ == '__main__':
    main()
