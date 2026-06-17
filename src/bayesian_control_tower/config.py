from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"

    # Prefix with litellm/ for non-Gemini models, e.g.:
    #   litellm/anthropic/claude-sonnet-4-6
    #   litellm/openai/gpt-4o
    default_model: str = "litellm/anthropic/claude-sonnet-4-6"

    anthropic_api_key: str = ""
    openai_api_key: str = ""
    google_api_key: str = ""

    agent_name: str = "bayesian-control-tower"
    agent_version: str = "0.1.0"


settings = Settings()
