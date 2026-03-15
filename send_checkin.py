"""
Send Check-in Command to SuperSong Bot
直接向机器人 @supersong_bot (ID: 481731051) 发送 /checkin 命令
"""
import asyncio
from telethon import TelegramClient
from src.config import config
from src.utils.logger import logger

# --- 配置区域 ---
BOT_ID = 12345678   # 机器人 ID
CHECKIN_COMMAND = "/checkin" # 签到命令
# ----------------

async def send_checkin():
    print("=" * 60)
    print("  Auto Check-in for @supersong_bot")
    print("=" * 60)
    
    session_path = config.get_session_path()
    
    # 代理配置 (保持与之前一致)
    # 如果你的代理是 HTTP，请将 'socks5' 改为 'http'
    proxy_config = ('socks5', '127.0.0.1', 3067)

    client = TelegramClient(
        session_path,
        config.API_ID,
        config.API_HASH,
        proxy=proxy_config
    )

    try:
        print(f"📡 Connecting to Telegram...")
        # start() 会自动加载已保存的会话，无需再次输入手机号
        await client.start()
        
        if not await client.is_user_authorized():
            print("❌ 未登录！请先运行 list_groups.py 进行登录。")
            return

        me = await client.get_me()
        print(f"✅ 当前用户: {me.first_name}")
        print(f"🤖 准备向机器人 (ID: {BOT_ID}) 发送命令: {CHECKIN_COMMAND}")
        print()

        # 发送消息
        # 使用 send_message 直接发给 ID
        result = await client.send_message(BOT_ID, CHECKIN_COMMAND)
        
        print("✅ 命令发送成功！")
        print(f"   消息时间: {result.date}")
        print(f"   消息 ID: {result.id}")
        print()
        print("💡 提示：请打开 Telegram 查看机器人的回复以确认签到结果。")

    except Exception as e:
        logger.error(f"❌ 发送失败: {e}", exc_info=True)
        print(f"\n❌ 发生错误: {e}")
        print("\n可能原因:")
        print("  1. 机器人 ID 错误或机器人已封禁")
        print("  2. 你从未与该机器人对话过 (请先在 Telegram 手动点一次 Start)")
        print("  3. 代理连接问题")
    
    finally:
        await client.disconnect()
        print("\n🔌 已断开连接")

def main():
    try:
        asyncio.run(send_checkin())
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断")
    except Exception as e:
        print(f"\n❌ 致命错误: {e}")

if __name__ == '__main__':
    main()