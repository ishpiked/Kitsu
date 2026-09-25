import logging
import sys
from typing import Any
import structlog
from app.config.settings import settings


def configure_logging() -> None:
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.JSONRenderer()
            if settings.is_production
            else structlog.dev.ConsoleRenderer(colors=True),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("telegram").setLevel(logging.INFO)


def get_logger(name: str) -> structlog.BoundLogger:
    return structlog.get_logger(name)


class LoggerMixin:
    @property
    def logger(self) -> structlog.BoundLogger:
        return get_logger(self.__class__.__module__)


def log_event(
    logger: structlog.BoundLogger,
    event: str,
    **kwargs: Any,
) -> None:
    logger.info(event, **kwargs)


def log_error(
    logger: structlog.BoundLogger,
    event: str,
    error: Exception,
    **kwargs: Any,
) -> None:
    logger.error(event, error=str(error), error_type=type(error).__name__, **kwargs)