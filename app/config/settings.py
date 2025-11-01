from pydantic import Field
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    """Manages application configuration settings.

    Loads settings from environment variables and an environment-specific
    .env file
    """

    APP_NAME: str
    HOST: str
    PORT: int = Field(ge=1, le=65535)
    DEBUG: bool = False
    EDEN_KEY: str

    model_config = SettingsConfigDict(
        env_file=".env"
    )


_settings: Settings | None = None


def get_settings() -> Settings:
    """
    Return a cached instance of the application settings.
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
