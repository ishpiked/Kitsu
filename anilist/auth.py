from urllib.parse import urlencode

import requests

from config.settings import (
    ANILIST_AUTHORIZE_URL,
    ANILIST_CLIENT_ID,
    ANILIST_CLIENT_SECRET,
    ANILIST_GRAPHQL_URL,
    ANILIST_REDIRECT_URI,
    ANILIST_TOKEN_URL,
)


def build_authorize_url(telegram_id: int) -> str:
    """Build AniList Authorization Code URL. `state` carries telegram_id."""
    params = {
        "client_id": ANILIST_CLIENT_ID,
        "redirect_uri": ANILIST_REDIRECT_URI,
        "response_type": "code",
        # telegram_id comes back as `state` in /callback so we know who logged in
        "state": str(telegram_id),
    }
    return f"{ANILIST_AUTHORIZE_URL}?{urlencode(params)}"


def exchange_code_for_token(code: str) -> str | None:
    """Exchange authorization `code` for a long-lived access token."""
    # AniList expects form-encoded body + HTTP Basic auth (client_id:client_secret),
    # NOT JSON body. JSON body gives {"error":"invalid_client"}.
    resp = requests.post(
        ANILIST_TOKEN_URL,
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": ANILIST_REDIRECT_URI,
        },
        auth=(str(ANILIST_CLIENT_ID), str(ANILIST_CLIENT_SECRET)),
        headers={"Accept": "application/json"},
        timeout=15,
    )
    if resp.status_code != 200:
        print(f"[auth] token exchange failed {resp.status_code}: {resp.text}")
        return None
    return resp.json().get("access_token")


def fetch_viewer_name(access_token: str) -> str | None:
    """Verify token by fetching Viewer { name }. Returns username or None."""
    resp = requests.post(
        ANILIST_GRAPHQL_URL,
        json={"query": "query { Viewer { name } }"},
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=15,
    )
    if resp.status_code != 200:
        return None
    try:
        return resp.json()["data"]["Viewer"]["name"]
    except (KeyError, TypeError):
        return None
