"""Temporary in-memory token store.

Works for local testing. On Vercel serverless this will NOT persist
between invocations — next slow step will swap this for Neon Postgres
or Upstash Redis behind the same get/save functions.
"""

_tokens: dict[int, str] = {}


def save_token(telegram_id: int, access_token: str) -> None:
    _tokens[telegram_id] = access_token


def get_token(telegram_id: int) -> str | None:
    return _tokens.get(telegram_id)
