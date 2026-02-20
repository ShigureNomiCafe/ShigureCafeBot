from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.request import HTTPXRequest

from src.config import TOKEN, PROXY_URL
from src.handlers import start_handler, audit_handler, chatid_handler
from src.utils.logger import logger, log_buffer_handler
from src.utils.http_client import HttpClient
from src.services.backend import BackendService

async def report_logs(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Task to report accumulated logs to the backend."""
    logs = log_buffer_handler.get_and_clear_buffer()
    if not logs:
        return
        
    try:
        await BackendService.upload_logs(logs)
    except Exception as e:
        # If upload fails, we might lose logs or we could put them back.
        # For now, we just log the failure.
        # Note: this log itself will be in the next batch (if it survives).
        logger.error(f"Failed to report logs to backend: {e}")

async def post_init(application) -> None:
    """Post initialization to setup global resources."""
    await HttpClient.get_client()
    
    # Schedule log reporting every 5 seconds
    if application.job_queue:
        application.job_queue.run_repeating(report_logs, interval=5, first=5)
        logger.info("Log reporting task scheduled every 5 seconds.")
    else:
        logger.warning("Job queue is not available. Log reporting task will not be scheduled.")

async def post_stop(application) -> None:
    """Post stop to cleanup global resources."""
    await HttpClient.close_client()

async def error_handler(update: object, context) -> None: 
    """Log the error and send a telegram message to notify the developer."""
    logger.error("Exception while handling an update:", exc_info=context.error)

def main():
    # Custom request with larger pool size and better timeouts
    request = HTTPXRequest(
        connection_pool_size=50,
        read_timeout=20,
        write_timeout=20,
        connect_timeout=20,
        pool_timeout=20,
        proxy=PROXY_URL if PROXY_URL else None
    )
    
    builder = ApplicationBuilder().token(TOKEN).request(request).get_updates_request(request)
    
    if PROXY_URL:
        logger.info(f"Telegram Bot is using proxy: {PROXY_URL}")
        
    application = builder.post_init(post_init).post_stop(post_stop).build()
    
    # Add handlers
    application.add_error_handler(error_handler)
    application.add_handler(CommandHandler('start', start_handler))
    application.add_handler(CommandHandler('chatid', chatid_handler))
    application.add_handler(CommandHandler('audit', audit_handler))
    
    logger.info("ShigureCafeBot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
