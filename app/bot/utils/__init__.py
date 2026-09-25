from telegram import Update
from telegram.ext import ContextTypes
from app.utils.logging import get_logger


logger = get_logger(__name__)


async def safe_edit_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    text: str,
    reply_markup=None,
    parse_mode: str | None = None,
) -> bool:
    if not update.callback_query:
        return False

    try:
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
        )
        return True
    except Exception as e:
        logger.warning("safe_edit_failed", error=str(e))
        return False


async def safe_answer_callback(
    update: Update,
    text: str | None = None,
    show_alert: bool = False,
) -> bool:
    if not update.callback_query:
        return False

    try:
        await update.callback_query.answer(text=text, show_alert=show_alert)
        return True
    except Exception as e:
        logger.warning("safe_answer_failed", error=str(e))
        return False


def get_user_id(update: Update) -> int | None:
    if update.effective_user:
        return update.effective_user.id
    return None


def get_chat_id(update: Update) -> int | None:
    if update.effective_chat:
        return update.effective_chat.id
    return None