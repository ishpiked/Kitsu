from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    BOT_TOKEN: str = Field(..., description="Telegram Bot Token from @BotFather")
    DATABASE_URL: str = Field(..., description="PostgreSQL async connection URL")
    REDIS_URL: str = Field(..., description="Redis connection URL")

    ANILIST_CLIENT_ID: str = Field(..., description="AniList OAuth Client ID")
    ANILIST_CLIENT_SECRET: str = Field(..., description="AniList OAuth Client Secret")
    ANILIST_REDIRECT_URI: str = Field(..., description="AniList OAuth Redirect URI")

    WEBHOOK_URL: str | None = Field(default=None, description="Production webhook URL")
    ENVIRONMENT: str = Field(default="development", description="Environment: development or production")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT.lower() == "development"


settings = Settings()