"""Detailed AniList user profile fetching."""

import re

import requests

from config.settings import ANILIST_GRAPHQL_URL

_PROFILE_QUERY = """
query {
  Viewer {
    id
    name
    siteUrl
    avatar { large }
    about
    statistics {
      anime { count episodesWatched meanScore }
      manga { count chaptersRead meanScore }
    }
  }
}
"""


def _clean_about(text: str | None, limit: int = 180) -> str | None:
    if not text:
        return None
    clean = re.sub(r"<[^>]+>", " ", text)
    clean = re.sub(r"\s+", " ", clean).strip()
    if not clean:
        return None
    if len(clean) > limit:
        cut = clean[:limit].rsplit(" ", 1)[0]
        clean = (cut if cut else clean[:limit]) + "..."
    return clean


def fetch_user_profile(access_token: str) -> dict | None:
    """Fetch detailed Viewer profile. Returns dict or None on failure."""
    resp = requests.post(
        ANILIST_GRAPHQL_URL,
        json={"query": _PROFILE_QUERY},
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=15,
    )
    if resp.status_code != 200:
        return None
    try:
        v = resp.json()["data"]["Viewer"]
        anime = v.get("statistics", {}).get("anime", {}) or {}
        manga = v.get("statistics", {}).get("manga", {}) or {}
        return {
            "id": v.get("id"),
            "name": v.get("name"),
            "site_url": v.get("siteUrl"),
            "avatar": (v.get("avatar") or {}).get("large"),
            "about": _clean_about(v.get("about")),
            "anime_count": anime.get("count", 0),
            "episodes_watched": anime.get("episodesWatched", 0),
            "anime_mean": anime.get("meanScore"),
            "manga_count": manga.get("count", 0),
            "chapters_read": manga.get("chaptersRead", 0),
            "manga_mean": manga.get("meanScore"),
        }
    except (KeyError, TypeError, AttributeError):
        return None
