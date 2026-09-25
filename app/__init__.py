from app.config.settings import settings
from app.utils.logging import configure_logging

configure_logging()

__all__ = ["settings"]