import os


def getenv(name: str, default: str = "") -> str:
    return os.getenv(name, default)


BOT_TOKEN = getenv("BOT_TOKEN")

ANILIST_CLIENT_ID = getenv("ANILIST_CLIENT_ID")
ANILIST_CLIENT_SECRET = getenv("ANILIST_CLIENT_SECRET")
# e.g. https://your-app.vercel.app/callback  (must match AniList client settings)
ANILIST_REDIRECT_URI = getenv("ANILIST_REDIRECT_URI")

ANILIST_AUTHORIZE_URL = "https://anilist.co/api/v2/oauth/authorize"
ANILIST_TOKEN_URL = "https://anilist.co/api/v2/oauth/token"
ANILIST_GRAPHQL_URL = "https://graphql.anilist.co"
