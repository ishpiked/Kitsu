from telegram.ext import Application, ApplicationBuilder, Defaults
from telegram import BotCommand, Update
from telegram.ext import ContextTypes
from app.config.settings import settings
from app.bot.handlers import get_start_handler
from app.utils.logging import get_logger


logger = get_logger(__name__)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("unhandled_error", error=str(context.error), error_type=type(context.error).__name__)


async def setup_bot_commands(application: Application) -> None:
    commands = [
        BotCommand("start", "Start the bot and sync your profile"),
    ]
    await application.bot.set_my_commands(commands)
    logger.info("bot_commands_set")


async def create_application() -> Application:
    application = (
        ApplicationBuilder()
        .token(settings.BOT_TOKEN)
        .defaults(Defaults(parse_mode="HTML"))
        .build()
    )

    application.add_handler(get_start_handler())
    application.add_error_handler(error_handler)

    await setup_bot_commands(application)

    logger.info("bot_application_created", environment=settings.ENVIRONMENT)
    return application


async def run_polling(application: Application) -> None:
    logger.info("starting_polling")
    await application.initialize()
    await application.start()
    await application.updater.start_polling(allowed_updates=["message", "callback_query"])

    import asyncio
    try:
        await asyncio.Event().wait()
    finally:
        await application.updater.stop()
        await application.stop()
        await application.shutdown()


async def setup_webhook(application: Application) -> None:
    if not settings.WEBHOOK_URL:
        raise ValueError("WEBHOOK_URL is required for webhook mode")

    webhook_url = f"{settings.WEBHOOK_URL}/webhook"
    await application.bot.set_webhook(url=webhook_url, allowed_updates=["message", "callback_query"])
    logger.info("webhook_set", url=webhook_url)