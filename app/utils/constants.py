from enum import Enum


class ButtonStyle(str, Enum):
    PRIMARY = "primary"
    SUCCESS = "success"
    DANGER = "danger"
    NEUTRAL = "neutral"


class CallbackPrefix(str, Enum):
    ANIME = "anime"
    MANGA = "manga"
    LIBRARY = "library"
    USER = "user"
    SETTINGS = "settings"
    AUTH = "auth"
    NAV = "nav"


class CallbackAction(str, Enum):
    VIEW = "view"
    ADD = "add"
    REMOVE = "remove"
    UPDATE = "update"
    LIST = "list"
    PAGE = "page"
    SETTINGS = "settings"
    LINK = "link"
    UNLINK = "unlink"
    BACK = "back"
    NEXT = "next"
    PREV = "prev"


MAX_CALLBACK_DATA_LENGTH = 64


WELCOME_MESSAGE = (
    "Welcome to AniList Bot.\n\n"
    "Your anime and manga library, directly inside Telegram.\n\n"
    "Setup is coming next."
)