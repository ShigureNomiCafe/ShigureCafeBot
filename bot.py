import os
import re
import logging
import httpx
import asyncio
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# Load environment variables
load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8080")
CAFE_API_KEY = os.getenv("CAFE_API_KEY")
AUDIT_GROUP_ID = os.getenv("AUDIT_GROUP_ID")
PROXY_URL = os.getenv("PROXY_URL")

# Backend API Base URL
API_BASE_URL = f"{BACKEND_URL.rstrip('/')}/api/v1"

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# UUID Regex
UUID_PATTERN = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.I)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    await update.message.reply_text(
        "你好！欢迎来到 Shigure Cafe 审核机器人。\n"
        "请使用命令 `/audit <审核码>` 来获取审核群邀请链接。\n"
        "例如：`/audit 12345678-1234-1234-1234-1234567890ab`\n"
        "审核码在你注册成功后会显示在网页上。",
        parse_mode='Markdown'
    )

async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /chatid command."""
    chat_id = update.effective_chat.id
    chat_type = update.effective_chat.type
    await update.message.reply_text(f"当前群组/聊天的 ID 是: `{chat_id}`\n类型: {chat_type}", parse_mode='Markdown')

async def audit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /audit command."""
    if update.effective_chat.type != 'private':
        await update.message.reply_text("为了保护隐私，请在与机器人的私聊中使用 `/audit` 命令。", parse_mode='Markdown')
        return

    if not context.args:
        await update.message.reply_text("使用方法：`/audit <审核码>`", parse_mode='Markdown')
        return

    audit_code = context.args[0].strip().lower()
    
    # Check if it looks like an audit code
    if not UUID_PATTERN.match(audit_code):
        await update.message.reply_text("请输入有效的审核码（格式如：xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx）。")
        return
    
    try:
        # Query backend with API Key
        headers = {}
        if CAFE_API_KEY:
            headers["Cafe-API-Key"] = CAFE_API_KEY
            
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{API_BASE_URL}/registrations/{audit_code}", 
                headers=headers
            )
        
        if response.status_code == 404:
            await update.message.reply_text("抱歉，找不到该审核码。请检查输入是否正确。" )
            return
        
        if response.status_code != 200:
            logger.error(f"Backend returned status {response.status_code}: {response.text}")
            await update.message.reply_text("后端服务请求失败，请稍后再试。" )
            return

        data = response.json()
        
        # Check status and expiration
        status = data.get("status")
        is_expired = data.get("isExpired", False)
        
        if status != "PENDING":
            await update.message.reply_text(f"该审核码状态为 {status}，无法重新获取链接。" )
            return
            
        if is_expired:
            await update.message.reply_text("该审核码已过期，请联系管理员或重新发起注册。" )
            return

        # Generate invite link
        if not AUDIT_GROUP_ID:
            await update.message.reply_text("未配置审核群 ID，请联系系统管理员。" )
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
            logger.error(f"Error creating invite link: {e}", exc_info=True)
            await update.message.reply_text("生成邀请链接失败，请确保机器人已加入审核群并拥有管理权限。" )

    except httpx.RequestError as e:
        logger.error(f"Backend request error: {e}", exc_info=True)
        await update.message.reply_text("连接后端服务器失败，请稍后再试。" )
    except Exception as e:
        logger.error(f"Unexpected error in audit handler: {e}", exc_info=True)
        await update.message.reply_text("发生未知错误，请稍后再试。" )

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    logger.error("Exception while handling an update:", exc_info=context.error)

if __name__ == '__main__':
    if not TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables.")
        exit(1)
        
    builder = ApplicationBuilder().token(TOKEN)
    if PROXY_URL:
        builder.proxy(PROXY_URL)
        builder.get_updates_proxy(PROXY_URL)
        logger.info(f"Telegram Bot is using proxy: {PROXY_URL}")
        
    application = builder.build()
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    start_handler = CommandHandler('start', start)
    chatid_handler = CommandHandler('chatid', get_chat_id)
    audit_handler = CommandHandler('audit', audit)
    
    application.add_handler(start_handler)
    application.add_handler(chatid_handler)
    application.add_handler(audit_handler)
    
    logger.info("ShigureCafeBot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)