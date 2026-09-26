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
            "hey! welcome to the bot.\n\n"
            "you're successfully connected to telegram."
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