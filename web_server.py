import os
import sys
import base64
import gzip
import asyncio
import boto3
from botocore.config import Config
from fastapi import FastAPI, HTTPException, Query, UploadFile, File
from telethon import TelegramClient
from dotenv import load_dotenv
import uvicorn

# 加载 .env
load_dotenv()

# ================= 配置区域 =================
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
SESSION_NAME = os.getenv("SESSION_NAME", "telegram_checkin")
BOT_ID = os.getenv("BOT_ID", "481731051")
COMMAND = os.getenv("COMMAND", "/checkin")
SECRET_KEY = os.getenv("SECRET_KEY", "change_me_secret")

# R2 配置 (从环境变量读取)
R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME")
R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
R2_OBJECT_KEY = os.getenv("R2_OBJECT_KEY", "telegram_checkin.session") # R2 里的文件名

# 路径配置
SESSION_DIR = "./sessions"
SESSION_FILE_PATH = os.path.join(SESSION_DIR, f"{SESSION_NAME}.session")

# ================= R2 客户端初始化 =================
def get_r2_client():
    if not all([R2_BUCKET_NAME, R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY]):
        return None
    
    # 构建 R2 的 S3 兼容端点
    endpoint_url = f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com"
    
    session = boto3.Session(
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_ACCESS_KEY,
    )
    
    s3 = session.client(
        's3',
        endpoint_url=endpoint_url,
        config=Config(signature_version='s3v4'),
        region_name='auto' # R2 不需要特定 region
    )
    return s3

# ================= 初始化逻辑 (核心) =================
def init_session_file():
    os.makedirs(SESSION_DIR, exist_ok=True)

    # 1. 检查本地是否存在
    if os.path.exists(SESSION_FILE_PATH):
        print(f"✅ 发现本地 Session 文件: {SESSION_FILE_PATH}")
        return True

    print("⚠️ 本地无 Session 文件，尝试从源恢复...")

    # 2. 尝试从 R2 下载
    if get_r2_client():
        print("🌐 尝试从 Cloudflare R2 下载 Session...")
        try:
            s3 = get_r2_client()
            obj = s3.get_object(Bucket=R2_BUCKET_NAME, Key=R2_OBJECT_KEY)
            data = obj['Body'].read()
            
            with open(SESSION_FILE_PATH, "wb") as f:
                f.write(data)
            
            print(f"✅ 成功从 R2 下载并保存 Session (大小: {len(data)} bytes)")
            return True
        except Exception as e:
            print(f"❌ R2 下载失败: {e}")
    
    # 3. 尝试从环境变量 (压缩版) 还原 (备用方案)
    encoded_session = os.getenv("COMPRESSED_SESSION_BASE64")
    if encoded_session:
        try:
            print("🔄 尝试从环境变量还原...")
            compressed_data = base64.b64decode(encoded_session)
            session_data = gzip.decompress(compressed_data)
            with open(SESSION_FILE_PATH, "wb") as f:
                f.write(session_data)
            print("✅ 从环境变量还原成功。")
            return True
        except Exception as e:
            print(f"⚠️ 环境变量还原失败: {e}")

    # 4. 如果都失败
    print("⚠️ 警告: 未找到 Session 文件 (本地/R2/Env 均无)。")
    print("⚠️ 服务将启动，请通过 POST /upload_session 接口上传文件。")
    return False

# ================= 签到逻辑 =================
async def run_checkin_task():
    if not os.path.exists(SESSION_FILE_PATH):
        return {"status": "error", "message": "Session file missing."}
    
    try:
        api_id_int = int(API_ID)
    except (ValueError, TypeError):
        return {"status": "error", "message": "Invalid API_ID"}

    client = TelegramClient(SESSION_FILE_PATH, api_id_int, API_HASH)
    try:
        await client.start()
        if not await client.is_user_authorized():
            return {"status": "error", "message": "User not authorized"}
        
        print(f"🚀 发送命令 {COMMAND} 到 {BOT_ID}")
        await client.send_message(BOT_ID, COMMAND)
        return {"status": "success", "message": "Checkin sent!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        await client.disconnect()

# ================= FastAPI 应用 =================
app = FastAPI(title="TG Auto Checkin (R2 Mode)")

@app.get("/")
def home():
    has_file = os.path.exists(SESSION_FILE_PATH)
    r2_configured = bool(get_r2_client())
    return {
        "status": "running", 
        "session_exists": has_file,
        "r2_enabled": r2_configured,
        "msg": "Ready." if has_file else "Waiting for session file (R2 or Upload)."
    }

@app.get("/trigger")
async def trigger(secret: str = Query(...)):
    if secret != SECRET_KEY:
        raise HTTPException(status_code=403, detail="Invalid secret")
    result = await run_checkin_task()
    return result

@app.post("/upload_session")
async def upload_session(file: UploadFile = File(...), secret: str = Query(...)):
    if secret != SECRET_KEY:
        raise HTTPException(status_code=403, detail="Invalid secret")
    if not file.filename.endswith(".session"):
        raise HTTPException(status_code=400, detail="Must be .session file")

    os.makedirs(SESSION_DIR, exist_ok=True)
    content = await file.read()
    with open(SESSION_FILE_PATH, "wb") as f:
        f.write(content)
    
    # 【可选】上传成功后，也可以反向同步回 R2，方便备份
    # 这里暂不实现，保持简单
    
    return {"status": "success", "message": "Uploaded! Please Restart service."}

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    init_session_file()
    print(f"🌐 Server starting on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)