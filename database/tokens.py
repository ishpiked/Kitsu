"""Temporary in-memory token store.

Works for local testing. On Vercel serverless this will NOT persist
between invocations — next slow step will swap this for Neon Postgres
or Upstash Redis behind the same get/save functions.
"""

_tokens: dict[int, str] = {}

# message_id of the last /login prompt per chat, so /callback can remove it.
_login_messages: dict[int, int] = {}


def save_token(telegram_id: int, access_token: str) -> None:
    _tokens[telegram_id] = access_token


def get_token(telegram_id: int) -> str | None:
    return _tokens.get(telegram_id)


def save_login_message(telegram_id: int, message_id: int) -> None:
    _login_messages[telegram_id] = message_id


def pop_login_message(telegram_id: int) -> int | None:
    return _login_messages.pop(telegram_id, None)
