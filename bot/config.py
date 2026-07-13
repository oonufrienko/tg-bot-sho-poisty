from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str
    gemini_api_key: str
    gemini_model: str = "gemini-2.5-flash"
    allowed_user_ids: str = ""
    database_path: str = "data/bot.db"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def allowed_ids(self) -> frozenset[int]:
        return frozenset(
            int(part) for part in self.allowed_user_ids.replace(" ", "").split(",") if part
        )

    @property
    def db_url(self) -> str:
        return f"sqlite+aiosqlite:///{self.database_path}"

    @property
    def db_url_sync(self) -> str:
        return f"sqlite:///{self.database_path}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
