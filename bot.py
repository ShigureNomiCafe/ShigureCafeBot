import os
import re
import logging
import requests
from datetime import datetime, timedelta, timezone
# ... (rest of imports)
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# Load environment variables
load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8080/api/v1")
CAFE_API_KEY = os.getenv("CAFE_API_KEY")
AUDIT_GROUP_ID = os.getenv("AUDIT_GROUP_ID")

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# UUID Regex
UUID_PATTERN = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.I)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    await update.message.reply_text(
        "你好！欢迎来到 Shigure Cafe 审核机器人。\n"
        "请发送你的审核码（Audit Code）来获取审核群邀请链接。\n"
        "审核码在你注册成功后会显示在网页上。"
    )

async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /chatid command."""
    chat_id = update.effective_chat.id
    chat_type = update.effective_chat.type
    await update.message.reply_text(f"当前群组/聊天的 ID 是: `{chat_id}`\n类型: {chat_type}", parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle private messages."""
    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()
    
    # Check if it looks like an audit code
    if not UUID_PATTERN.match(text):
        await update.message.reply_text("请输入有效的审核码（格式如：xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx）。")
        return

    audit_code = text.lower()
    
    try:
        # Query backend with API Key
        headers = {}
        if CAFE_API_KEY:
            headers["Cafe-API-Key"] = CAFE_API_KEY
            
        response = requests.get(
            f"{BACKEND_API_URL}/registrations/{audit_code}", 
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 404:
            await update.message.reply_text("抱歉，找不到该审核码。请检查输入是否正确。")
            return
        
        if response.status_code != 200:
            await update.message.reply_text("后端服务请求失败，请稍后再试。")
            return

        data = response.json()
        
        # Check status and expiration
        status = data.get("status")
        is_expired = data.get("isExpired", False)
        
        if status != "PENDING":
            await update.message.reply_text(f"该审核码状态为 {status}，无法重新获取链接。")
            return
            
        if is_expired:
            await update.message.reply_text("该审核码已过期，请联系管理员或重新发起注册。")
            return

        # Generate invite link
        if not AUDIT_GROUP_ID:
            await update.message.reply_text("未配置审核群 ID，请联系系统管理员。")
            return

        try:
            # 10 minutes from now (UTC)
            expire_date = datetime.now(timezone.utc) + timedelta(minutes=10)
            
            invite_link = await context.bot.create_chat_invite_link(
                chat_id=AUDIT_GROUP_ID,
                expire_date=expire_date,
                member_limit=1,
                name=f"Audit: {data.get('username')}"
            )
            
            await update.message.reply_text(
                f"验证成功！\n"
                f"用户：{data.get('username')}\n\n"
                f"这是你的专属审核群邀请链接（10分钟内有效，仅限使用一次）：\n"
                f"{invite_link.invite_link}"
            )
            
        except Exception as e:
            logging.error(f"Error creating invite link: {e}")
            await update.message.reply_text("生成邀请链接失败，请确保机器人已加入审核群并拥有管理权限。")

    except requests.exceptions.RequestException as e:
        logging.error(f"Backend request error: {e}")
        await update.message.reply_text("连接后端服务器失败，请稍后再试。")

if __name__ == '__main__':
    if not TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not found in environment variables.")
        exit(1)
        
    application = ApplicationBuilder().token(TOKEN).build()
    
    start_handler = CommandHandler('start', start)
    chatid_handler = CommandHandler('chatid', get_chat_id)
    msg_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)
    
    application.add_handler(start_handler)
    application.add_handler(chatid_handler)
    application.add_handler(msg_handler)
    
    print("ShigureCafeBot is running...")
    application.run_polling()
