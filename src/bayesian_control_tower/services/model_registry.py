"""Model registry — maps logical names to LiteLLM model strings.

ADK 2.x uses LiteLLM under the hood for non-Gemini providers.
Format for non-Google models: "litellm/<provider>/<model-id>"

Usage:
    registry = ModelRegistry.default()
    model_str = registry.resolve("claude-sonnet")
"""

from pydantic import BaseModel


class ModelConfig(BaseModel):
    alias: str
    litellm_model: str
    provider: str
    description: str = ""


# Central catalogue — extend as needed
_CATALOGUE: list[ModelConfig] = [
    ModelConfig(
        alias="claude-sonnet",
        litellm_model="litellm/anthropic/claude-sonnet-4-6",
        provider="anthropic",
        description="Anthropic Claude Sonnet 4.6 — default reasoning model",
    ),
    ModelConfig(
        alias="claude-opus",
        litellm_model="litellm/anthropic/claude-opus-4-8",
        provider="anthropic",
        description="Anthropic Claude Opus 4.8 — highest capability",
    ),
    ModelConfig(
        alias="gpt-4o",
        litellm_model="litellm/openai/gpt-4o",
        provider="openai",
        description="OpenAI GPT-4o",
    ),
    ModelConfig(
        alias="gemini-flash",
        litellm_model="gemini-2.0-flash",
        provider="google",
        description="Google Gemini 2.0 Flash — fast, cost-efficient",
    ),
    ModelConfig(
        alias="gemini-pro",
        litellm_model="gemini-2.5-pro",
        provider="google",
        description="Google Gemini 2.5 Pro",
    ),
]


class ModelRegistry:
    def __init__(self, models: list[ModelConfig]) -> None:
        self._models: dict[str, ModelConfig] = {m.alias: m for m in models}

    @classmethod
    def default(cls) -> "ModelRegistry":
        return cls(_CATALOGUE)

    def resolve(self, alias: str) -> str:
        """Return the LiteLLM model string for a given alias.

        Falls through transparently if alias is already a full model string.
        """
        if alias in self._models:
            return self._models[alias].litellm_model
        return alias

    def list_models(self) -> list[ModelConfig]:
        return list(self._models.values())

    def by_provider(self, provider: str) -> list[ModelConfig]:
        return [m for m in self._models.values() if m.provider == provider]
