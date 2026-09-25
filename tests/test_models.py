import pytest
from datetime import datetime
from app.database.models import User


def test_user_model():
    user = User(
        telegram_id=123456789,
        telegram_username="testuser",
        first_name="Test",
        last_name="User",
        anilist_user_id=987654321,
        is_active=True,
    )
    assert user.telegram_id == 123456789
    assert user.telegram_username == "testuser"
    assert user.first_name == "Test"
    assert user.last_name == "User"
    assert user.anilist_user_id == 987654321
    assert user.is_active is True


def test_user_model_optional_fields():
    user = User(
        telegram_id=123456789,
        first_name="Test",
        is_active=True,
    )
    assert user.telegram_id == 123456789
    assert user.first_name == "Test"
    assert user.telegram_username is None
    assert user.last_name is None
    assert user.anilist_user_id is None
    assert user.is_active is True