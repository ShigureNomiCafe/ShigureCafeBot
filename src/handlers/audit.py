import re
from datetime import datetime, timedelta, timezone
from telegram import Update
from telegram.ext import ContextTypes
from src.config import AUDIT_GROUP_ID
from src.services.backend import BackendService
from src.utils.logger import logger

UUID_PATTERN = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.I)

async def audit_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /audit command."""
    if update.effective_chat.type != 'private':
        await update.message.reply_text("为了保护隐私，请在与机器人的私聊中使用 `/audit` 命令。", parse_mode='Markdown')
        return

    if not context.args:
        await update.message.reply_text("使用方法：`/audit <审核码>`", parse_mode='Markdown')
        return

    audit_code = context.args[0].strip().lower()
    
    if not UUID_PATTERN.match(audit_code):
        await update.message.reply_text("请输入有效的审核码（格式如：xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx）。")
        return
    
    try:
        response = await BackendService.get_registration(audit_code)
        
        if response.status_code == 404:
            await update.message.reply_text("抱歉，找不到该审核码。请检查输入是否正确。" )
            return
        
        if response.status_code != 200:
            logger.error(f"Backend returned status {response.status_code}: {response.text}")
            await update.message.reply_text("后端服务请求失败，请稍后再试。" )
            return

        data = response.json()
        status = data.get("status")
        is_expired = data.get("isExpired", False)
        
        if status != "PENDING":
            await update.message.reply_text(f"该审核码状态为 {status}，无法重新获取链接。" )
            return
            
        if is_expired:
            await update.message.reply_text("该审核码已过期，请联系管理员或重新发起注册。" )
            return

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

    except Exception as e:
        logger.error(f"Unexpected error in audit handler: {e}", exc_info=True)
        await update.message.reply_text("处理请求时发生错误，请稍后再试。" )
