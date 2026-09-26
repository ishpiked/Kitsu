import os
import requests
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

from anilist.auth import build_authorize_url, exchange_code_for_token, fetch_viewer_name
from database.tokens import get_token, save_token

app = FastAPI()

BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"


def send_message(chat_id: int, text: str) -> None:
    if not BOT_TOKEN:
        return
    requests.post(
        f"{TELEGRAM_API}/sendMessage",
        json={"chat_id": chat_id, "text": text},
        timeout=10,
    )


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

    elif text == "/login":
        login_url = build_authorize_url(chat_id)
        send_message(
            chat_id,
            f"Tap to connect your AniList account:\n{login_url}\n\n"
            "After approving, you'll land back here and I'll confirm you're linked.",
        )

    elif text == "/me":
        token = get_token(chat_id)
        if not token:
            send_message(chat_id, "You're not linked yet. Send /login to connect.")
        else:
            name = fetch_viewer_name(token)
            if name:
                send_message(chat_id, f"You're linked as {name} ✅")
            else:
                send_message(chat_id, "Your token looks expired. Send /login again.")

    return {"ok": True}


@app.get("/callback")
async def callback(code: str = "", state: str = ""):
    """AniList redirects here after user approves. `state` = telegram chat_id."""
    if not code or not state:
        return HTMLResponse("<h3>Missing code. Try /login again in Telegram.</h3>", status_code=400)

    try:
        chat_id = int(state)
    except ValueError:
        return HTMLResponse("<h3>Invalid session. Try /login again.</h3>", status_code=400)

    token = exchange_code_for_token(code)
    if not token:
        return HTMLResponse("<h3>Login failed. Try /login again.</h3>", status_code=400)

    name = fetch_viewer_name(token)
    if not name:
        return HTMLResponse("<h3>Could not verify account. Try again.</h3>", status_code=400)

    save_token(chat_id, token)
    send_message(chat_id, f"You're linked as {name} ✅ You can now use /me.")

    return HTMLResponse(
        f"<h3>Linked as {name} ✅</h3><p>You can go back to Telegram.</p>"
    )


@app.get("/")
async def root():
    return {"status": "online"}