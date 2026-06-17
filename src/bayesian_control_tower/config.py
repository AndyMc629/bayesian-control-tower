from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"

    # ADK model string format:
    #   Anthropic (direct):  claude-sonnet-4-6   (no prefix — ADK has native Claude support)
    #   OpenAI (via LiteLLM): openai/gpt-4o      (provider/ prefix, no litellm/ prefix)
    #   Gemini (direct):     gemini-2.0-flash    (no prefix)
    default_model: str = "openai/gpt-4o"

    anthropic_api_key: str = ""
    openai_api_key: str = ""
    google_api_key: str = ""

    agent_name: str = "bayesian-control-tower"
    agent_version: str = "0.1.0"


settings = Settings()
