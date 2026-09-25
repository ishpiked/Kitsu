from fastapi import APIRouter, Request, Response
from telegram import Update
from app.bot import create_application
from app.config.settings import settings
from app.utils.logging import get_logger


logger = get_logger(__name__)

router = APIRouter()


async def get_bot_application():
    return await create_application()


@router.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/webhook")
async def webhook(request: Request) -> Response:
    application = await get_bot_application()

    try:
        data = await request.json()
        update = Update.de_json(data, application.bot)
        await application.process_update(update)
        return Response(content="OK", status_code=200)
    except Exception as e:
        logger.error("webhook_error", error=str(e))
        return Response(content="Error", status_code=500)
    finally:
        await application.shutdown()