from telegram import Update
from telegram.ext import ContextTypes

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    await update.message.reply_text(
        "你好！欢迎来到 Shigure Cafe 审核机器人。\n"
        "请使用命令 `/audit <审核码>` 来获取审核群邀请链接。\n"
        "例如：`/audit 12345678-1234-1234-1234-1234567890ab`\n"
        "审核码在你注册成功后会显示在网页上。",
        parse_mode='Markdown'
    )

