from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler
from telegram.request import HTTPXRequest

from src.config import TOKEN, PROXY_URL
from src.handlers import start_handler, audit_handler, chatid_handler
from src.utils.logger import logger
from src.utils.http_client import HttpClient

async def post_init(application) -> None:
    """Post initialization to setup global resources."""
    await HttpClient.get_client()

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
        pool_timeout=20
    )
    
    builder = ApplicationBuilder().token(TOKEN).request(request)
    
    if PROXY_URL:
        builder.proxy(PROXY_URL)
        builder.get_updates_proxy(PROXY_URL)
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
