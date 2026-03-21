from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # ── Anthropic ──────────────────────────────────────
    anthropic_api_key: str = Field(..., env="ANTHROPIC_API_KEY")
    anthropic_model: str = "claude-sonnet-4-20250514"
    anthropic_max_tokens: int = 4096

    # ── OpenAI (optional — for future use) ────────────
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o", env="OPENAI_MODEL")

    # ── GitHub ─────────────────────────────────────────
    github_token: str = Field(..., env="GITHUB_TOKEN")
    github_webhook_secret: str = Field(..., env="GITHUB_WEBHOOK_SECRET")
    github_repo_owner: str = Field(..., env="GITHUB_REPO_OWNER")
    github_repo_name: str = Field(..., env="GITHUB_REPO_NAME")

    # ── Redis ──────────────────────────────────────────
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")

    # ── App ────────────────────────────────────────────
    app_env: str = Field(default="development", env="APP_ENV")
    app_port: int = Field(default=8000, env="APP_PORT")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()