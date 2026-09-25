from fastapi import FastAPI
from app.api import api_router
from app.utils.logging import get_logger, configure_logging

configure_logging()
logger = get_logger(__name__)

app = FastAPI(
    title="AniList Telegram Bot",
    description="Telegram bot for AniList integration",
    version="1.0.0",
)

app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "AniList Telegram Bot API", "docs": "/docs"}


@app.get("/health")
async def health():
    return {"status": "ok"}