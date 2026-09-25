# Middleware support was added in python-telegram-bot 22+
# For now, we use handler-level error handling and logging
# This will be updated when upgrading to a version with middleware support

from typing import Callable, Awaitable, Any
from telegram import Update
from telegram.ext import ContextTypes
from app.utils.logging import get_logger


logger = get_logger(__name__)


async def logging_wrapper(
    handler: Callable[[Update, ContextTypes.DEFAULT_TYPE], Awaitable[Any]],
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> Any:
    user = update.effective_user
    chat = update.effective_chat

    log_context = {
        "update_id": update.update_id,
        "user_id": user.id if user else None,
        "username": user.username if user else None,
        "chat_id": chat.id if chat else None,
        "chat_type": chat.type if chat else None,
    }

    if update.message:
        log_context["message_id"] = update.message.message_id
        log_context["command"] = update.message.text
    elif update.callback_query:
        log_context["callback_data"] = update.callback_query.data
        log_context["callback_id"] = update.callback_query.id

    logger.info("update_received", **log_context)

    try:
        return await handler(update, context)
    except Exception as e:
        logger.error("update_handler_error", error=str(e), error_type=type(e).__name__, **log_context)
        raise


async def error_handling_wrapper(
    handler: Callable[[Update, ContextTypes.DEFAULT_TYPE], Awaitable[Any]],
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> Any:
    try:
        return await handler(update, context)
    except Exception as e:
        logger.error("unhandled_error", error=str(e), error_type=type(e).__name__)
        raise