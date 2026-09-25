import asyncio
import sys
from app.config.settings import settings
from app.bot import create_application, run_polling
from app.utils.logging import get_logger


logger = get_logger(__name__)


async def main():
    application = await create_application()

    if settings.is_development:
        await run_polling(application)
    else:
        logger.info("production_mode_detected_use_uvicorn")
        sys.exit(0)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("bot_stopped")