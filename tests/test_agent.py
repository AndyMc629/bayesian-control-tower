"""Tests for agent creation, memory service, and model registry."""

import pytest

from bayesian_control_tower.services.model_registry import ModelConfig, ModelRegistry


class TestModelRegistry:
    def test_default_registry_has_entries(self) -> None:
        registry = ModelRegistry.default()
        assert len(registry.list_models()) > 0

    def test_resolve_alias(self) -> None:
        registry = ModelRegistry.default()
        resolved = registry.resolve("claude-sonnet")
        assert "anthropic" in resolved

    def test_resolve_passthrough(self) -> None:
        registry = ModelRegistry.default()
        raw = "litellm/openai/gpt-4o-custom"
        assert registry.resolve(raw) == raw

    def test_by_provider(self) -> None:
        registry = ModelRegistry.default()
        anthropic_models = registry.by_provider("anthropic")
        assert all(m.provider == "anthropic" for m in anthropic_models)
        assert len(anthropic_models) >= 1

    def test_custom_registry(self) -> None:
        custom = ModelRegistry(
            [ModelConfig(alias="my-model", litellm_model="litellm/openai/gpt-4", provider="openai")]
        )
        assert custom.resolve("my-model") == "litellm/openai/gpt-4"


class TestAgentMemoryService:
    """Smoke tests for the in-memory session service wrapper."""

    @pytest.mark.asyncio
    async def test_creates_session(self) -> None:
        from bayesian_control_tower.agent.memory import AgentMemoryService

        svc = AgentMemoryService(app_name="test-app")
        session = await svc.get_or_create_session(user_id="user-1", session_id="sess-1")
        assert session is not None
        assert session.id == "sess-1"

    @pytest.mark.asyncio
    async def test_get_existing_session(self) -> None:
        from bayesian_control_tower.agent.memory import AgentMemoryService

        svc = AgentMemoryService(app_name="test-app")
        s1 = await svc.get_or_create_session(user_id="user-1", session_id="sess-2")
        s2 = await svc.get_or_create_session(user_id="user-1", session_id="sess-2")
        assert s1.id == s2.id


class TestBayesianAgentCreation:
    """Ensure the ADK agent can be instantiated without network calls."""

    def test_create_with_default_model(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("DEFAULT_MODEL", "litellm/anthropic/claude-sonnet-4-6")
        from bayesian_control_tower.agent.bayesian_agent import create_bayesian_agent

        agent = create_bayesian_agent()
        assert agent.name == "bayesian_control_layer"

    def test_create_with_explicit_model(self) -> None:
        from bayesian_control_tower.agent.bayesian_agent import create_bayesian_agent

        agent = create_bayesian_agent(model="litellm/openai/gpt-4o")
        assert agent is not None
