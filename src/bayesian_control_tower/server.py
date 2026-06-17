"""A2A server entry point.

Builds the protobuf AgentCard, wires the A2A request handler and executor,
and returns a Starlette ASGI app. Run via:

    uv run serve
    # or with auto-reload:
    uvicorn bayesian_control_tower.server:app --reload
"""

import uvicorn
from a2a.server.request_handlers.default_request_handler_v2 import DefaultRequestHandlerV2
from a2a.server.routes.rest_routes import create_rest_routes
from a2a.server.tasks.inmemory_task_store import InMemoryTaskStore
from a2a.types.a2a_pb2 import AgentCapabilities, AgentCard, AgentSkill
from google.protobuf.json_format import MessageToDict
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from bayesian_control_tower.agent.executor import BayesianAgentExecutor
from bayesian_control_tower.config import settings

_AGENT_CARD = AgentCard(
    name=settings.agent_name,
    description=(
        "Bayesian control layer for multi-agent systems. "
        "Accepts agent-state snapshots and decision points; "
        "returns probabilistically ranked next-step recommendations."
    ),
    version=settings.agent_version,
    capabilities=AgentCapabilities(),
    skills=[
        AgentSkill(
            id="bayesian_advice",
            name="Bayesian Advisory",
            description=(
                "Given the current states of agents in a multi-agent system "
                "and a decision point, return Bayesian posterior-ranked recommendations."
            ),
            input_modes=["text"],
            output_modes=["text"],
        ),
    ],
    default_input_modes=["text"],
    default_output_modes=["text"],
)


def build_app() -> Starlette:
    executor = BayesianAgentExecutor()
    handler = DefaultRequestHandlerV2(
        agent_executor=executor,
        task_store=InMemoryTaskStore(),
        agent_card=_AGENT_CARD,
    )

    a2a_routes = create_rest_routes(request_handler=handler)

    async def agent_card_handler(request: Request) -> JSONResponse:
        return JSONResponse(MessageToDict(_AGENT_CARD))

    return Starlette(
        routes=[Route("/.well-known/agent.json", agent_card_handler, methods=["GET"])] + a2a_routes
    )


app = build_app()


def main() -> None:
    uvicorn.run(
        "bayesian_control_tower.server:app",
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
        reload=False,
    )


if __name__ == "__main__":
    main()
