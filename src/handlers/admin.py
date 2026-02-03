from telegram import Update
from telegram.ext import ContextTypes

async def chatid_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /chatid command."""
    chat_id = update.effective_chat.id
    chat_type = update.effective_chat.type
    await update.message.reply_text(f"当前群组/聊天的 ID 是: `{chat_id}`\n类型: {chat_type}", parse_mode='Markdown')
