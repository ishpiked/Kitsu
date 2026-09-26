"""Public AniList catalog search: anime, manga, characters."""

import re

import requests

from config.settings import ANILIST_GRAPHQL_URL

_MEDIA_FIELDS = """
id
title { romaji english }
siteUrl
coverImage { large }
description
averageScore
genres
format
status
episodes
chapters
volumes
startDate { year }
relations {
  edges {
    relationType
    node { id title { romaji } siteUrl type }
  }
}
"""

_SEARCH_MEDIA = (
    "query ($q: String, $type: MediaType, $n: Int) {"
    " Page(perPage: $n) { media(search: $q, type: $type) {" + _MEDIA_FIELDS + "} } }"
)

_MEDIA_BY_ID = "query ($id: Int) { Media(id: $id) {" + _MEDIA_FIELDS + "} }"

_NEXT_AIRING = (
    "query ($q: String) { Media(search: $q, type: ANIME) {"
    " id title { romaji english } siteUrl"
    " nextAiringEpisode { episode airingAt timeUntilAiring } } }"
)

_SCHEDULE = (
    "query ($from: Int, $to: Int, $n: Int) {"
    " Page(perPage: $n) { airingSchedules("
    " airingAt_greater: $from, airingAt_lesser: $to, sort: TIME) {"
    " episode airingAt timeUntilAiring"
    " media { title { romaji english } siteUrl } } } }"
)

_SEARCH_STUDIOS = (
    "query ($q: String, $n: Int) {"
    " Page(perPage: $n) { studios(search: $q) {"
    " id name siteUrl"
    " media(sort: POPULARITY_DESC, perPage: 3) { nodes { title { romaji } } }"
    " } } }"
)
_SEARCH_CHARACTER = (
    "query ($q: String, $n: Int) {"
    " Page(perPage: $n) { characters(search: $q) {"
    " id name { full } siteUrl image { large }"
    " media(perPage: 3) { nodes { title { romaji } type } }"
    " } } }"
)


def _post(query: str, variables: dict) -> dict | None:
    try:
        resp = requests.post(
            ANILIST_GRAPHQL_URL,
            json={"query": query, "variables": variables},
            timeout=15,
        )
    except Exception:
        return None
    if resp.status_code != 200:
        return None
    try:
        return resp.json()["data"]
    except (KeyError, TypeError, ValueError):
        return None


def clean_description(text: str | None, limit: int = 450) -> str | None:
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


def media_title(m: dict) -> str:
    t = m.get("title") or {}
    return t.get("english") or t.get("romaji") or "Unknown"


def search_media(query: str, media_type: str, per_page: int = 5) -> list[dict]:
    data = _post(_SEARCH_MEDIA, {"q": query, "type": media_type, "n": per_page})
    if not data:
        return []
    try:
        return data["Page"]["media"] or []
    except (KeyError, TypeError):
        return []


def search_characters(query: str, per_page: int = 5) -> list[dict]:
    data = _post(_SEARCH_CHARACTER, {"q": query, "n": per_page})
    if not data:
        return []
    try:
        return data["Page"]["characters"] or []
    except (KeyError, TypeError):
        return []


def prequel_sequel(m: dict) -> tuple[dict | None, dict | None]:
    pre, seq = None, None
    try:
        edges = m.get("relations", {}).get("edges", []) or []
    except AttributeError:
        return None, None
    for e in edges:
        node = e.get("node") or {}
        if (node.get("type") or "") != "ANIME":
            continue
        if e.get("relationType") == "PREQUEL" and pre is None:
            pre = node
        elif e.get("relationType") == "SEQUEL" and seq is None:
            seq = node
    return pre, seq


def search_studios(query: str, per_page: int = 5) -> list[dict]:
    data = _post(_SEARCH_STUDIOS, {"q": query, "n": per_page})
    if not data:
        return []
    try:
        return data["Page"]["studios"] or []
    except (KeyError, TypeError):
        return []


def next_airing(query: str) -> dict | None:
    data = _post(_NEXT_AIRING, {"q": query})
    if not data:
        return None
    try:
        return data["Media"]
    except (KeyError, TypeError):
        return None


def airing_soon(from_ts: int, to_ts: int, per_page: int = 10) -> list[dict]:
    data = _post(_SCHEDULE, {"from": from_ts, "to": to_ts, "n": per_page})
    if not data:
        return []
    try:
        return data["Page"]["airingSchedules"] or []
    except (KeyError, TypeError):
        return []
