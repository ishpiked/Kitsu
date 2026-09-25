import pytest
from app.config.settings import Settings


def test_settings_load():
    settings = Settings(
        BOT_TOKEN="test_token",
        DATABASE_URL="postgresql+asyncpg://user:pass@localhost/db",
        REDIS_URL="redis://localhost:6379/0",
        ANILIST_CLIENT_ID="client_id",
        ANILIST_CLIENT_SECRET="client_secret",
        ANILIST_REDIRECT_URI="http://localhost/callback",
    )
    assert settings.BOT_TOKEN == "test_token"
    assert settings.is_development
    assert not settings.is_production


def test_settings_production():
    settings = Settings(
        BOT_TOKEN="test_token",
        DATABASE_URL="postgresql+asyncpg://user:pass@localhost/db",
        REDIS_URL="redis://localhost:6379/0",
        ANILIST_CLIENT_ID="client_id",
        ANILIST_CLIENT_SECRET="client_secret",
        ANILIST_REDIRECT_URI="http://localhost/callback",
        ENVIRONMENT="production",
    )
    assert settings.is_production
    assert not settings.is_development