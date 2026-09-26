import os
import requests
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

from anilist.auth import build_authorize_url, exchange_code_for_token, fetch_viewer, fetch_viewer_name
from database.tokens import get_token, save_token

app = FastAPI()

PAGE_CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: -apple-system, 'Segoe UI', Roboto, Overpass, sans-serif;
  background: #0b1622 radial-gradient(ellipse 80% 60% at 50% -10%, #1e3a5f 0%, transparent 60%);
  color: #edf1f5;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}
.card {
  background: #151f2e;
  border-radius: 16px;
  padding: 48px 40px 40px;
  max-width: 420px;
  width: 100%;
  text-align: center;
  box-shadow: 0 20px 60px rgba(0,0,0,.5);
  border: 1px solid rgba(61,180,242,.15);
}
.badge {
  width: 72px; height: 72px;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 34px; margin: 0 auto 20px;
}
.badge.ok { background: rgba(46, 204, 113, .15); border: 2px solid #2ecc71; }
.badge.err { background: rgba(231, 76, 60, .12); border: 2px solid #e74c3c; }
.avatar {
  width: 84px; height: 84px; border-radius: 50%;
  object-fit: cover; margin: 0 auto 16px; display: block;
  border: 3px solid #3db4f2;
}
h1 { font-size: 22px; font-weight: 700; margin-bottom: 8px; }
h1 .user { color: #3db4f2; }
p { color: #9fadbd; font-size: 15px; line-height: 1.6; }
p.hint {
  margin-top: 20px; padding-top: 20px;
  border-top: 1px solid rgba(255,255,255,.07);
  font-size: 13px;
}
.btn {
  display: inline-block; margin-top: 24px;
  background: #3db4f2; color: #0b1622;
  font-weight: 700; font-size: 15px;
  padding: 12px 32px; border-radius: 10px;
  text-decoration: none; transition: transform .15s, box-shadow .15s;
}
.btn:hover { transform: translateY(-1px); box-shadow: 0 8px 24px rgba(61,180,242,.4); }
.brand { margin-top: 28px; font-size: 12px; color: #647380; letter-spacing: .5px; }
.brand b { color: #3db4f2; }
"""


def success_page(name: str, avatar: str | None) -> str:
    img = f'<img class="avatar" src="{avatar}" alt="{name}" />' if avatar else '<div class="badge ok">✓</div>'
    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8" /><meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Linked to AniList</title><style>{PAGE_CSS}</style></head>
<body><div class="card">
{img}
<h1>Linked as <span class="user">{name}</span></h1>
<p>Your AniList account is connected.<br />Your lists will now stay in sync via Telegram.</p>
<a class="btn" href="https://t.me/">Back to Telegram</a>
<p class="hint">You can safely close this tab and return to your chat.</p>
<div class="brand"><b>Kitsu</b> • AniList on Telegram</div>
</div></body></html>"""


def error_page(title: str, detail: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8" /><meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Login failed</title><style>{PAGE_CSS}</style></head>
<body><div class="card">
<div class="badge err">✕</div>
<h1>{title}</h1>
<p>{detail}</p>
<p class="hint">Go back to Telegram and send <b>/login</b> to try again with a fresh link.</p>
<div class="brand"><b>Kitsu</b> • AniList on Telegram</div>
</div></body></html>"""

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
        return HTMLResponse(error_page("Missing code", "The login link was incomplete."), status_code=400)

    try:
        chat_id = int(state)
    except ValueError:
        return HTMLResponse(error_page("Invalid session", "Could not match this login to your chat."), status_code=400)

    token = exchange_code_for_token(code)
    if not token:
        return HTMLResponse(error_page("Login failed", "AniList rejected the login code. Codes expire fast and work only once."), status_code=400)

    viewer = fetch_viewer(token)
    if not viewer:
        return HTMLResponse(error_page("Could not verify account", "Got a token but couldn't read your AniList profile."), status_code=400)

    save_token(chat_id, token)
    send_message(chat_id, f"You're linked as {viewer['name']} ✅ You can now use /me.")

    return HTMLResponse(success_page(viewer["name"], viewer.get("avatar")))


@app.get("/")
async def root():
    return {"status": "online"}