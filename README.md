# 📱 Telegram Auto Check-In System

A fully automated Telegram check-in bot that sends daily check-in messages to multiple groups and automatically retries until success is detected. Built with Telethon for maximum compatibility with human-verification groups.

## ✨ Features

- 🤖 **UserBot Authentication**: Uses your personal Telegram account (not a bot) to bypass human-verification
- ⏰ **Smart Scheduling**: Automatic check-in at 00:00 Singapore time (configurable timezone)
- 🔄 **Retry Logic**: Automatically retries every hour until success is detected
- 🎯 **Keyword Detection**: Monitors replies for success keywords like "签到成功", "获得", "积分"
- 📊 **Comprehensive Logging**: Detailed logs for debugging and monitoring
- ☁️ **Cloud Ready**: Easy deployment to Railway or Fly.io with persistent storage
- 🔒 **Session Persistence**: Login once, session saved for automatic reconnection

## 📋 Prerequisites

Before you begin, you need:

1. **Telegram API Credentials**
   - Visit [my.telegram.org/apps](https://my.telegram.org/apps)
   - Log in with your phone number
   - Create a new application
   - Save your `API_ID` and `API_HASH`

2. **Python 3.11+** (for local development)
3. **Docker** (for containerized deployment)

## 🚀 Quick Start

### Step 1: Clone and Setup

```bash
# Navigate to your project directory
cd "C:\Users\Administrator\Desktop\Tg自动签到"

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment

1. Copy the example environment file:
   ```bash
   copy .env.example .env
   ```

2. Edit `.env` with your credentials:
   ```env
   # Get these from https://my.telegram.org/apps
   API_ID=12345678
   API_HASH=your_api_hash_here
   
   # Your phone number with country code
   PHONE_NUMBER=+1234567890
   
   # Group IDs (see Step 3 below)
   GROUP_IDS=-1001234567890,-1009876543210
   
   # Check-in message
   CHECKIN_MESSAGE=签到
   
   # Timezone
   TIMEZONE=Asia/Singapore
   
   # Success detection keywords
   KEYWORDS=签到,成功,积分,获得
   ```

### Step 3: Find Your Group IDs

Run the group discovery script:

```bash
python list_groups.py
```

This will:
1. Authenticate with your account (first time only)
2. List all groups and channels you've joined
3. Display their IDs for easy copy-paste

**Example output:**
```
═══════════════════════════════════════════════════════
📱 GROUPS (3 found)
═══════════════════════════════════════════════════════

1. 签到群组
   ID: -1001234567890
   Type: Group

2. 积分奖励群
   ID: -1009876543210
   Type: Group
```

Copy the IDs you want and add them to `.env`:
```env
GROUP_IDS=-1001234567890,-1009876543210
```

### Step 4: Run Locally

```bash
python src/main.py
```

**First-time login:**
- You'll be prompted for your phone number
- Enter the verification code sent to your Telegram app
- Session will be saved in `session/` directory
- Future runs will use the saved session automatically

**What you'll see:**
```
═══════════════════════════════════════════════════════
  Telegram Auto Check-In System
  Version 1.0.0
═══════════════════════════════════════════════════════

🤖 Initializing Telegram Check-In Bot...
   Timezone: Asia/Singapore
   Groups: 2
   Keywords: 签到, 成功, 积分, 获得

✓ Successfully authenticated with Telegram
✓ Logged in as: YourName (@yourusername)
✓ Scheduled daily check-in at 00:00 Singapore time
✓ Scheduled hourly retry check

═══════════════════════════════════════════════════════
✅ BOT INITIALIZED SUCCESSFULLY
═══════════════════════════════════════════════════════

🚀 Scheduler started
   Waiting for scheduled tasks...

📅 Daily Check-In at 00:00
   Next run: 2025-12-05 00:00:00 SGT

📅 Hourly Retry Check
   Next run: 2025-12-04 19:00:00 SGT

═══════════════════════════════════════════════════════
🟢 BOT IS RUNNING
   Press Ctrl+C to stop
═══════════════════════════════════════════════════════
```

## 🔍 How It Works

### Daily Check-In Flow

1. **00:00 Singapore Time**: Bot wakes up and starts check-in process
2. **Send Messages**: Sends "签到" to all configured groups
3. **Monitor Replies**: Listens for 3 minutes for any reply messages
4. **Detect Success**: Checks if any reply contains keywords like "签到成功", "获得", "积分"
5. **Success**: ✅ Check-in complete, wait until next day
6. **Failure**: ⚠️ Retry in 1 hour

### Retry Logic

- If success is not detected, bot retries **every hour** automatically
- Retries continue indefinitely until success keyword is found
- Once successful, retries stop until the next day at 00:00
- Each attempt is logged with timestamp and results

### Example Log Output

```
═══════════════════════════════════════════════════════
🚀 Starting check-in process (Retry #0)
   Time: 2025-12-05 00:00:00
═══════════════════════════════════════════════════════
📋 Groups to check-in: 2
📤 Sending check-in to group -1001234567890...
   Group: 签到群组
✓ Message sent: '签到'
📤 Sending check-in to group -1009876543210...
   Group: 积分奖励群
✓ Message sent: '签到'

📡 Monitoring 2 groups for success replies...
   Looking for keywords: 签到, 成功, 积分, 获得
✓ Success keyword detected: '签到'
   Message: 签到成功！获得10积分...
═══════════════════════════════════════════════════════
✅ CHECK-IN SUCCESSFUL!
   Keywords detected: 签到
═══════════════════════════════════════════════════════
```

## ☁️ Cloud Deployment

### Option 1: Railway (Recommended)

Railway provides easy deployment with persistent volumes.

#### Steps:

1. **Install Railway CLI** (optional):
   ```bash
   npm i -g @railway/cli
   railway login
   ```

2. **Deploy via GitHub** (easier):
   - Push your code to GitHub (make sure to exclude `.env` and `session/`)
   - Go to [Railway](https://railway.app)
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Railway will detect `Dockerfile` automatically

3. **Configure Environment Variables**:
   - In Railway dashboard, go to your service
   - Click "Variables" tab
   - Add all variables from your `.env` file:
     - `API_ID`
     - `API_HASH`
     - `PHONE_NUMBER`
     - `GROUP_IDS`
     - `CHECKIN_MESSAGE`
     - `TIMEZONE`
     - `KEYWORDS`

4. **Important: Set up Volumes**:
   - Go to "Settings" → "Volumes"
   - Add a new volume:
     - **Mount Path**: `/app/session`
     - **Size**: 1GB
   - This ensures your session persists across deployments

5. **Initial Login**:
   - First deployment will fail because session doesn't exist
   - Railway doesn't support interactive input for verification codes
   - **Solution**: Run locally first to create the session file
   - Then manually upload the session file to Railway volume
   - Or use a local Docker container to create the session, then deploy

6. **Monitor Logs**:
   - Click "View Logs" to see real-time output
   - Check for successful initialization

### Option 2: Fly.io

Fly.io offers great pricing and global regions.

#### Steps:

1. **Install Fly CLI**:
   ```bash
   # Windows (PowerShell)
   iwr https://fly.io/install.ps1 -useb | iex
   
   # Login
   fly auth login
   ```

2. **Create App**:
   ```bash
   cd "C:\Users\Administrator\Desktop\Tg自动签到"
   fly launch --no-deploy
   ```
   
   When prompted:
   - App name: `telegram-checkin` (or your choice)
   - Region: `sin` (Singapore)
   - Don't deploy yet: select "No"

3. **Create Volumes for Persistence**:
   ```bash
   # Create volume for session files
   fly volumes create telegram_session --size 1 --region sin
   
   # Create volume for logs
   fly volumes create telegram_logs --size 1 --region sin
   ```

4. **Set Environment Variables**:
   ```bash
   fly secrets set API_ID=your_api_id
   fly secrets set API_HASH=your_api_hash
   fly secrets set PHONE_NUMBER=+1234567890
   fly secrets set GROUP_IDS=-1001234567890,-1009876543210
   fly secrets set CHECKIN_MESSAGE=签到
   fly secrets set TIMEZONE=Asia/Singapore
   fly secrets set KEYWORDS=签到,成功,积分,获得
   ```

5. **Deploy**:
   ```bash
   fly deploy
   ```

6. **Initial Login Issue**:
   - Same as Railway, Fly.io can't handle interactive login
   - Create session locally first
   - Use `fly ssh console` to access the container
   - Upload session file via `fly sftp shell`

7. **Monitor**:
   ```bash
   fly logs
   fly status
   ```

### Handling Session Files in Cloud

**Problem**: Cloud platforms don't support interactive input for Telegram verification codes.

**Solutions**:

1. **Local Session Creation** (Recommended):
   ```bash
   # Run locally to create session
   python src/main.py
   # Enter phone and verification code
   # Session saved to session/telegram_checkin.session
   
   # Then deploy to cloud with session file in volume
   ```

2. **Docker Local**:
   ```bash
   # Build image
   docker build -t telegram-checkin .
   
   # Run interactively to create session
   docker run -it -v ${PWD}/session:/app/session telegram-checkin
   
   # Then deploy the session directory to cloud
   ```

3. **Cloud Console Access**:
   - Some platforms allow SSH access to containers
   - You can log in and run the app interactively once
   - Session persists in the volume

## 📝 Configuration Reference

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `API_ID` | ✅ Yes | - | Your Telegram API ID from my.telegram.org |
| `API_HASH` | ✅ Yes | - | Your Telegram API Hash from my.telegram.org |
| `PHONE_NUMBER` | ✅ Yes | - | Your phone number with country code (e.g., +1234567890) |
| `GROUP_IDS` | ✅ Yes | - | Comma-separated group IDs to send check-in messages |
| `CHECKIN_MESSAGE` | ❌ No | `签到` | Message to send for check-in |
| `TIMEZONE` | ❌ No | `Asia/Singapore` | Timezone for scheduling (pytz format) |
| `KEYWORDS` | ❌ No | `签到,成功,积分,获得` | Keywords to detect success in replies |

### Timezone Options

Common timezone values:
- `Asia/Singapore` (UTC+8)
- `Asia/Shanghai` (UTC+8)
- `Asia/Hong_Kong` (UTC+8)
- `UTC` (UTC+0)
- `America/New_York` (EST/EDT)

See [pytz documentation](https://pypi.org/project/pytz/) for full list.

## 🔧 Troubleshooting

### "Configuration validation failed"
- Make sure all required variables are set in `.env`
- Check that `API_ID` is a number (no quotes)
- Verify `GROUP_IDS` format: `-1001234567890,-1009876543210`

### "Failed to authenticate"
- Verify `API_ID` and `API_HASH` are correct
- Make sure phone number includes country code: `+1234567890`
- Delete `session/` folder and try logging in again

### "Cannot write to group"
- You don't have permission to send messages in that group
- Verify the group ID is correct
- Make sure you're not banned or restricted

### "Flood wait error"
- Telegram is rate-limiting your account
- The bot will automatically wait and retry
- Consider reducing the number of groups

### "No success keywords detected"
- Check that reply messages actually contain the keywords
- Adjust `KEYWORDS` in `.env` to match your groups' responses
- Increase `MONITOR_TIMEOUT` in `src/config.py` if replies are slow

### Session file not persisting in cloud
- Make sure volumes are properly configured
- Verify mount paths match: `/app/session`
- Check volume size is sufficient (1GB recommended)

## 📂 Project Structure

```
Tg自动签到/
├── src/
│   ├── __init__.py
│   ├── main.py              # Main application entry point
│   ├── auth.py              # Telethon authentication
│   ├── checkin.py           # Check-in execution and retry logic
│   ├── monitor.py           # Message monitoring for success detection
│   ├── config.py            # Configuration loader
│   └── utils/
│       ├── __init__.py
│       └── logger.py        # Logging utility
├── session/                 # Session files (auto-created, gitignored)
├── logs/                    # Log files (auto-created, gitignored)
├── list_groups.py           # Group discovery script
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker configuration
├── railway.json             # Railway deployment config
├── fly.toml                 # Fly.io deployment config
├── .env.example             # Environment template
├── .env                     # Your environment (create this, gitignored)
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## 🛡️ Security Notes

- **Never commit** `.env` file or `session/` directory to Git
- Session files contain your authentication token - keep them secure
- Use environment variables in cloud deployments (never hardcode credentials)
- Be aware that UserBots operate on your personal account
- Telegram may rate-limit if you send too many messages

## 📜 License

This project is for educational purposes. Make sure to comply with Telegram's Terms of Service when using UserBots.

## 🤝 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review logs in `logs/app.log`
3. Make sure all prerequisites are met
4. Verify your Telegram API credentials

## 🎯 Tips for Success

- **Test locally first** before deploying to cloud
- **Use list_groups.py** to find correct group IDs
- **Monitor logs** for the first 24 hours to ensure everything works
- **Adjust keywords** based on your groups' actual reply messages
- **Keep session files** backed up in case of cloud issues
- **Check timezone** settings match your desired schedule

---

**Built with ❤️ using Telethon and Python**
