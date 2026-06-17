"""Tests for the A2A server app construction and agent card endpoint."""

import pytest
from httpx import ASGITransport, AsyncClient

from bayesian_control_tower.server import build_app


@pytest.fixture
def app():
    return build_app()


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


class TestAgentCard:
    @pytest.mark.asyncio
    async def test_agent_card_endpoint(self, client: AsyncClient) -> None:
        response = await client.get("/.well-known/agent.json")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_agent_card_content(self, client: AsyncClient) -> None:
        response = await client.get("/.well-known/agent.json")
        card = response.json()
        assert card["name"] == "bayesian-control-tower"
        assert "skills" in card
        assert len(card["skills"]) >= 1

    @pytest.mark.asyncio
    async def test_agent_card_has_bayesian_skill(self, client: AsyncClient) -> None:
        response = await client.get("/.well-known/agent.json")
        skills = response.json()["skills"]
        skill_ids = [s["id"] for s in skills]
        assert "bayesian_advice" in skill_ids


class TestAppConstruction:
    def test_build_app_returns_starlette_app(self) -> None:
        from starlette.applications import Starlette

        app = build_app()
        assert isinstance(app, Starlette)

    def test_build_app_is_idempotent(self) -> None:
        app1 = build_app()
        app2 = build_app()
        assert type(app1) is type(app2)
