from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from sqlalchemy import select
from app.database.database import get_session
from app.database.models import User
from app.utils.logging import get_logger
from app.utils.constants import WELCOME_MESSAGE
from app.bot.keyboards import primary_button, build_keyboard


logger = get_logger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_user or not update.message:
        return

    telegram_user = update.effective_user

    async for session in get_session():
        try:
            stmt = select(User).where(User.telegram_id == telegram_user.id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            if user:
                user.telegram_username = telegram_user.username
                user.first_name = telegram_user.first_name or ""
                user.last_name = telegram_user.last_name
                user.is_active = True
                logger.info("user_updated", telegram_id=telegram_user.id)
            else:
                user = User(
                    telegram_id=telegram_user.id,
                    telegram_username=telegram_user.username,
                    first_name=telegram_user.first_name or "",
                    last_name=telegram_user.last_name,
                    is_active=True,
                )
                session.add(user)
                logger.info("user_created", telegram_id=telegram_user.id)

            await session.commit()

        except Exception as e:
            await session.rollback()
            logger.error("start_command_db_error", telegram_id=telegram_user.id, error=str(e))
            await update.message.reply_text("An error occurred. Please try again later.")
            return

    keyboard = build_keyboard([
        [primary_button("Get Started", "nav:get_started")],
    ])

    await update.message.reply_text(WELCOME_MESSAGE, reply_markup=keyboard)


def get_start_handler() -> CommandHandler:
    return CommandHandler("start", start_command)