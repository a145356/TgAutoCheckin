import os
import sys
import base64
import asyncio
from fastapi import FastAPI, HTTPException, Query
from telethon import TelegramClient
from dotenv import load_dotenv

# 加载 .env 文件 (本地开发用，Railway 上主要靠环境变量)
load_dotenv()

# ================= 配置区域 =================
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_NAME = os.getenv("SESSION_NAME", "telegram_checkin") # 对应你的文件名前缀
BOT_ID = int(os.getenv("BOT_ID", "123475678"))
COMMAND = os.getenv("COMMAND", "/checkin")
SECRET_KEY = os.getenv("SECRET_KEY", "change_me_secret")

# Session 文件路径
SESSION_DIR = "./sessions"
SESSION_FILE_PATH = os.path.join(SESSION_DIR, f"{SESSION_NAME}.session")

# ================= 初始化 Session 文件 =================
def init_session_file():
    """如果 session 文件不存在，尝试从环境变量解码生成"""
    if not os.path.exists(SESSION_FILE_PATH):
        os.makedirs(SESSION_DIR, exist_ok=True)
        encoded_session = os.getenv("SESSION_FILE_BASE64")
        
        if encoded_session:
            try:
                print("🔄 正在从环境变量还原 Session 文件...")
                session_data = base64.b64decode(encoded_session)
                with open(SESSION_FILE_PATH, "wb") as f:
                    f.write(session_data)
                print(f"✅ Session 文件已成功还原到: {SESSION_FILE_PATH}")
            except Exception as e:
                print(f"❌ 还原 Session 失败: {e}")
                sys.exit(1)
        else:
            print("❌ 错误: 未找到 Session 文件，且未提供 SESSION_FILE_BASE64 环境变量")
            sys.exit(1)
    else:
        print(f"✅ 检测到现有 Session 文件: {SESSION_FILE_PATH}")

# ================= 核心签到逻辑 =================
async def run_checkin_task():
    """执行 Telethon 签到任务"""
    client = TelegramClient(SESSION_FILE_PATH, API_ID, API_HASH)
    
    try:
        await client.start()
        if not await client.is_user_authorized():
            return {"status": "error", "message": "用户未授权，Session 可能已失效"}
        
        print(f"🚀 正在向机器人 {BOT_ID} 发送命令: {COMMAND}")
        await client.send_message(BOT_ID, COMMAND)
        print("✅ 命令发送成功！")
        return {"status": "success", "message": f"已向 {BOT_ID} 发送 {COMMAND}"}
    
    except Exception as e:
        error_msg = str(e)
        print(f"❌ 发生错误: {error_msg}")
        return {"status": "error", "message": error_msg}
    finally:
        await client.disconnect()

# ================= FastAPI 服务 =================
app = FastAPI()

@app.get("/")
def read_root():
    return {
        "service": "TgAutoCheckin-Web",
        "status": "running",
        "target_bot": BOT_ID
    }

@app.get("/trigger")
async def trigger_checkin(secret: str = Query(...)):
    """
    触发签到的接口
    用法: GET /trigger?secret=你的密钥
    """
    if secret != SECRET_KEY:
        raise HTTPException(status_code=403, detail="Invalid secret key")
    
    # 执行异步任务
    result = await run_checkin_task()
    
    if result["status"] == "success":
        return result
    else:
        # 即使业务逻辑失败，也返回 200 OK 给 Cloudflare，避免触发重试风暴
        # 具体错误信息在 body 中
        return result

if __name__ == "__main__":
    import uvicorn
    # Railway 会自动注入 PORT 环境变量
    port = int(os.getenv("PORT", "8000"))
    
    print("🔧 正在初始化环境...")
    init_session_file()
    
    print(f"🌐 服务启动在端口 {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)