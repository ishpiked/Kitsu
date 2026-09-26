import os
import requests
from fastapi import FastAPI, Request

app = FastAPI()

BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"


@app.post("/webhook")
async def webhook(request: Request):
    update = await request.json()

    message = update.get("message")

    if not message:
        return {"ok": True}

    text = message.get("text", "")
    chat_id = message["chat"]["id"]

    if text == "/start":
        welcome_message = (
            """Welcome to AniList Bot.

Your personal anime and manga companion, now available directly on Telegram. Connect your AniList account and explore a complete catalog of anime and manga, discover new titles, view detailed information, and keep track of everything you're watching or reading.

You can search for titles, explore characters, studios, genres, and recommendations, check what's currently airing, and manage your AniList library without leaving Telegram.

Get started by connecting your AniList account and explore everything AniList has to offer, right from your chat.
"""
        )

        requests.post(
            f"{TELEGRAM_API}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": welcome_message
            },
            timeout=10
        )

    return {"ok": True}


@app.get("/")
async def root():
    return {"status": "online"}