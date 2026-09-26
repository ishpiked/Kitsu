import html
import os
import requests
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

from anilist.auth import build_authorize_url, exchange_code_for_token, fetch_viewer, fetch_viewer_name
from database.tokens import get_token, save_token

app = FastAPI()

LOGO_SVG = """<span class="logo"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640" fill="none" aria-hidden="true"><defs><linearGradient id="catGradient" x1="215" y1="175" x2="425" y2="450" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#ED1235"/><stop offset="0.48" stop-color="#F32245"/><stop offset="1" stop-color="#FF526C"/></linearGradient></defs><style>.eye{transform-box:fill-box;transform-origin:center;animation:blink 5s ease-in-out infinite}.eye.right{animation-delay:.03s}@keyframes blink{0%,43%,48%,100%{transform:scaleY(1)}45%,46.5%{transform:scaleY(.06)}}.whisker{transform-box:fill-box;transform-origin:center;animation:whiskerMove 3.2s ease-in-out infinite}.whisker.left.lower{animation-delay:.18s}.whisker.right{animation-delay:.12s}.whisker.right.lower{animation-delay:.27s}@keyframes whiskerMove{0%,100%{transform:rotate(0)}25%{transform:rotate(-2.5deg)}50%{transform:rotate(1.5deg)}75%{transform:rotate(-1deg)}}.cat-head{transform-box:fill-box;transform-origin:center;animation:headFloat 4s ease-in-out infinite}@keyframes headFloat{0%,100%{transform:translateY(0)}50%{transform:translateY(-2px)}}</style><g class="cat-head"><path fill="url(#catGradient)" d="M223.5 175.5Q221 177 218.5 181.5Q216 186 215 205.5Q214 225 220 231.5Q226 238 224.5 239.5Q223 241 219 242.5Q215 244 214 247Q213 250 217.5 254.5Q222 259 217 263.5Q212 268 212 276Q212 284 211 288.5Q210 293 204 300.5Q198 308 194 314.5Q190 321 186 334Q182 347 181.5 355Q181 363 182 371Q183 379 186 388Q189 397 194.5 406Q200 415 207.5 422.5Q215 430 221 434Q227 438 237 442Q247 446 255.5 447.5Q264 449 311.5 449Q359 449 371.5 446Q384 443 393.5 438Q403 433 414 422Q425 411 429 404Q433 397 436 388Q439 379 440 368Q441 357 440 349.5Q439 342 436.5 334.5Q434 327 434 321.5Q434 316 442.5 275Q451 234 451 231.5Q451 229 449.5 226Q448 223 445 220.5Q442 218 437.5 217.5Q433 217 428.5 219.5Q424 222 392.5 245.5Q361 269 356.5 270.5Q352 272 339.5 272Q327 272 323.5 271Q320 270 315.5 266Q311 262 277 220.5Q243 179 239.5 176.5Q236 174 231 174Q226 174 223.5 175.5Z"/><g class="eye left"><path fill="#FFFFFF" d="M291 361C291 394 278 415 251 415C222 415 204 394 204 363C204 331 224 309 252 309C278 309 291 331 291 361Z"/><path fill="url(#catGradient)" d="M282 367C282 385 275 398 264 398C253 398 245 385 245 367C245 349 253 336 264 336C275 336 282 349 282 367Z"/></g><g class="eye right"><path fill="#FFFFFF" d="M420 363C420 395 403 415 375 415C346 415 329 394 329 364C329 331 348 309 375 309C403 309 420 332 420 363Z"/><path fill="url(#catGradient)" d="M379 369C379 387 372 400 361 400C350 400 343 387 343 369C343 351 350 338 361 338C372 338 379 351 379 369Z"/></g></g><g class="whisker left"><path d="M160 398 L174 394" stroke="url(#catGradient)" stroke-width="9" stroke-linecap="round"/></g><g class="whisker left lower"><path d="M153 434 L179 420" stroke="url(#catGradient)" stroke-width="9" stroke-linecap="round"/></g><g class="whisker right"><path d="M450 394 L463 398" stroke="url(#catGradient)" stroke-width="9" stroke-linecap="round"/></g><g class="whisker right lower"><path d="M461 420 L486 434" stroke="url(#catGradient)" stroke-width="9" stroke-linecap="round"/></g></svg></span>"""

FONT_HEAD = """<link rel="preconnect" href="https://fonts.googleapis.com" /><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin /><link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,200..800&display=swap" rel="stylesheet" />"""

PAGE_CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: 'Bricolage Grotesque', -apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, Roboto, sans-serif;
  background: #0D0D0F;
  color: #FFFFFF;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  justify-content: flex-start;
  padding: 0;
  -webkit-font-smoothing: antialiased;
}
.sitehead {
  display: flex; align-items: center; gap: 10px;
  padding: 18px 22px;
}
.sitehead .logo { display: inline-flex; width: 46px; height: 46px; }
.sitehead .logo svg { width: 100%; height: 100%; display: block; }
.sitehead .name { font-size: 17px; font-weight: 800; letter-spacing: .2px; line-height: 1.1; }
.sitehead .name small { display: block; font-size: 9px; font-weight: 700; letter-spacing: 2px; color: #A5A5AA; margin-top: 3px; }
.wrap {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px 20px 28px;
}
.card {
  background: #161619;
  border: 1px solid #29292E;
  border-radius: 18px;
  max-width: 400px;
  width: 100%;
  overflow: hidden;
}
.pill {
  font-size: 11px; font-weight: 700; letter-spacing: 1px;
  padding: 5px 10px; border-radius: 999px;
}
.pill.ok { color: #F21D45; background: rgba(242,29,69,.12); border: 1px solid rgba(242,29,69,.35); }
.pill.err { color: #A5A5AA; background: transparent; border: 1px solid #29292E; }
.main { padding: 28px 24px 24px; text-align: left; }
.ava {
  width: 60px; height: 60px; border-radius: 16px;
  object-fit: cover; display: block;
  border: 1px solid #29292E;
  margin-bottom: 18px;
}
.mark {
  width: 48px; height: 48px; border-radius: 14px;
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 18px; border: 1px solid #29292E;
  background: #0D0D0F;
}
.mark svg { display: block; }
.eyebrow {
  font-size: 11px; font-weight: 700; letter-spacing: 1.5px;
  color: #A5A5AA; margin-bottom: 8px;
}
.statusrow { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
.statusrow .eyebrow { margin-bottom: 0; }
h1 { font-size: 24px; font-weight: 800; letter-spacing: -0.5px; line-height: 1.2; }
h1 span { color: #FF4968; }
.sub { color: #A5A5AA; font-size: 14px; line-height: 1.6; margin-top: 10px; }
.userline {
  display: flex; align-items: center; gap: 10px;
  margin-top: 18px; padding: 12px 14px;
  background: #0D0D0F; border: 1px solid #29292E; border-radius: 12px;
  font-size: 14px;
}
.userline .dot { width: 8px; height: 8px; border-radius: 50%; background: #F21D45; flex-shrink: 0; }
.userline b { font-weight: 650; }
.userline small { color: #A5A5AA; margin-left: auto; font-size: 12px; }
.btn {
  display: block; text-align: center; margin-top: 20px;
  background: #F21D45; color: #FFFFFF;
  font-weight: 700; font-size: 14px;
  padding: 14px; border-radius: 12px;
  text-decoration: none;
}
.btn:active { background: #c81638; }
.ghost {
  display: block; text-align: center; margin-top: 10px;
  color: #A5A5AA; font-size: 13px; text-decoration: none;
  padding: 10px;
}
.foot { padding: 14px 20px; border-top: 1px solid #29292E; font-size: 12px; color: #A5A5AA; }
@media (max-width: 440px) { .main { padding: 24px 20px 20px; } }
"""


def success_page(name: str, avatar: str | None, user_id: int | None = None) -> str:
    if avatar:
        visual = f'<img class="ava" src="{avatar}" alt="" />'
    else:
        visual = (
            '<div class="mark"><svg width="22" height="22" viewBox="0 0 24 24" fill="none">'
            '<path d="M4 12.5l5 5L20 6.5" stroke="#F21D45" stroke-width="2.5" '
            'stroke-linecap="round" stroke-linejoin="round"/></svg></div>'
        )
    idtag = f"<small>ID {user_id}</small>" if user_id else "<small>AniList</small>"
    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8" /><meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Connected — Kitsu</title>{FONT_HEAD}<style>{PAGE_CSS}</style></head>
<body><header class="sitehead">{LOGO_SVG}<div class="name">Kitsu<small>ANILIST ON TELEGRAM</small></div></header><div class="wrap"><div class="card">
<div class="main">
<div class="statusrow"><div class="eyebrow">ANILIST ACCOUNT</div><div class="pill ok">CONNECTED</div></div>
{visual}
<h1>You&rsquo;re in, <span>{name}</span></h1>
<p class="sub">Account linked. Anything you update from Telegram syncs straight to your AniList.</p>
<div class="userline"><span class="dot"></span><b>{name}</b>{idtag}</div>
<a class="btn" href="https://t.me/AniKitsuBot">Return to Telegram</a>
</div>
<div class="foot">You can close this tab now.</div>
</div></div></body></html>"""


def error_page(title: str, detail: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8" /><meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Login failed — Kitsu</title>{FONT_HEAD}<style>{PAGE_CSS}</style></head>
<body><header class="sitehead">{LOGO_SVG}<div class="name">Kitsu<small>ANILIST ON TELEGRAM</small></div></header><div class="wrap"><div class="card">
<div class="main">
<div class="statusrow"><div class="eyebrow">LOGIN ISSUE</div><div class="pill err">FAILED</div></div>
<div class="mark"><svg width="20" height="20" viewBox="0 0 24 24" fill="none">
<path d="M6 6l12 12M18 6L6 18" stroke="#A5A5AA" stroke-width="2.2" stroke-linecap="round"/></svg></div>
<h1>{title}</h1>
<p class="sub">{detail}</p>
<a class="btn" href="https://t.me/AniKitsuBot">Back to Telegram</a>
<a class="ghost" href="https://t.me/AniKitsuBot">Send /login again for a fresh link</a>
</div>
<div class="foot">Codes expire fast and work only once.</div>
</div></div></body></html>"""

BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"


def send_message(chat_id: int, text: str, reply_markup: dict | None = None) -> None:
    if not BOT_TOKEN:
        return
    payload: dict = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if reply_markup is not None:
        payload["reply_markup"] = reply_markup
    requests.post(
        f"{TELEGRAM_API}/sendMessage",
        json=payload,
        timeout=10,
    )


def login_keyboard(login_url: str) -> dict:
    return {"inline_keyboard": [[{"text": "Connect AniList Account", "url": login_url}]]}


@app.post("/webhook")
async def webhook(request: Request):
    update = await request.json()

    message = update.get("message")

    if not message:
        return {"ok": True}

    text = message.get("text") or ""
    chat_id = message["chat"]["id"]

    if text == "/start":
        send_message(
            chat_id,
            "<b>Kitsu, AniList on Telegram.</b>\n"
            "\n"
            "Welcome. Kitsu brings your AniList library to Telegram so you can search anime and manga, view details, and manage your lists without leaving chat.\n"
            "\n"
            "To unlock list updates and sync, connect your AniList account first.\n"
            "\n"
            "<b>Begin here:</b>\n"
            "Send /login to connect your account.\n"
            "Send /me to check your link status.\n"
            "\n"
            "Your lists stay in sync with AniList whenever you update them here.",
        )

    elif text == "/login":
        login_url = build_authorize_url(chat_id)
        send_message(
            chat_id,
            "<b>Connect your AniList account.</b>\n"
            "\n"
            "Tap the button below to open AniList and approve access for Kitsu. After approval you will return here and Kitsu will confirm the link.\n"
            "\n"
            "If the button does not open, send /login again for a fresh link. Links expire fast and work only once.",
            reply_markup=login_keyboard(login_url),
        )

    elif text == "/me":
        token = get_token(chat_id)
        if not token:
            send_message(
                chat_id,
                "<b>No linked account found.</b>\n"
                "\n"
                "Kitsu cannot read your lists yet because no AniList account is connected to this chat.\n"
                "\n"
                "Send /login to connect your account, then try /me again.",
            )
        else:
            name = fetch_viewer_name(token)
            if name:
                safe_name = html.escape(name)
                send_message(
                    chat_id,
                    f"<b>Linked account: {safe_name}.</b>\n"
                    "\n"
                    "Kitsu is connected to this AniList profile. Updates you make here will sync to your AniList lists.\n"
                    "\n"
                    "Use /login any time to switch accounts.",
                )
            else:
                send_message(
                    chat_id,
                    "<b>Link check failed.</b>\n"
                    "\n"
                    "The saved token for this chat is expired or invalid, so Kitsu cannot reach your AniList profile right now.\n"
                    "\n"
                    "Send /login to connect again with a fresh link.",
                )

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
    safe_name = html.escape(viewer["name"])
    send_message(
        chat_id,
        f"<b>Account linked: {safe_name}.</b>\n"
        "\n"
        "Kitsu is now connected to this AniList profile. You can close the browser tab and return to chat.\n"
        "\n"
        "Send /me to verify your link any time.",
    )

    return HTMLResponse(success_page(viewer["name"], viewer.get("avatar"), viewer.get("id")))


@app.get("/")
async def root():
    return {"status": "online"}