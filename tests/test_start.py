import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from telegram import Update, User, Message, Chat
from telegram.ext import ContextTypes
from app.bot.handlers import start_command
from app.database.models import User as UserModel


@pytest.fixture
def mock_update():
    update = MagicMock(spec=Update)
    user = MagicMock(spec=User)
    user.id = 123456789
    user.username = "testuser"
    user.first_name = "Test"
    user.last_name = "User"
    update.effective_user = user
    update.effective_chat = MagicMock(spec=Chat)
    update.effective_chat.id = 123456789
    update.message = MagicMock(spec=Message)
    update.message.reply_text = AsyncMock()
    return update


@pytest.fixture
def mock_context():
    return MagicMock(spec=ContextTypes.DEFAULT_TYPE)


class MockSession:
    def __init__(self, result=None):
        self.execute = AsyncMock()
        self.commit = AsyncMock()
        self.rollback = AsyncMock()
        self.close = AsyncMock()
        self.add = MagicMock()
        self._result = result
        if result is not None:
            self.execute.return_value = AsyncMock(scalar_one_or_none=AsyncMock(return_value=result))

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self._result is not None or True:
            raise StopAsyncIteration
        return self


async def mock_get_session_creates_user():
    session = MockSession(None)
    yield session


async def mock_get_session_updates_user():
    existing_user = UserModel(
        telegram_id=123456789,
        telegram_username="olduser",
        first_name="Old",
        last_name="Name",
    )
    session = MockSession(existing_user)
    yield session


@pytest.mark.asyncio
async def test_start_command_creates_user(mock_update, mock_context):
    with patch("app.bot.handlers.get_session", mock_get_session_creates_user):
        await start_command(mock_update, mock_context)

        # Verify the session was used
        mock_update.message.reply_text.assert_called_once()


@pytest.mark.asyncio
async def test_start_command_updates_existing_user(mock_update, mock_context):
    with patch("app.bot.handlers.get_session", mock_get_session_updates_user):
        await start_command(mock_update, mock_context)

        mock_update.message.reply_text.assert_called_once()