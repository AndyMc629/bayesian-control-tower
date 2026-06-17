"""A2A AgentExecutor — immediate-response pattern.

Runs the ADK agent and returns a single Message event. This is the simplest
valid A2A executor flow: no task state machine, one response per request.

Upgrade path: swap to the Task-based flow (enqueue Task → status updates →
artifact → complete) when streaming or long-running behaviour is needed.
"""

import uuid

import structlog
from a2a.helpers.proto_helpers import get_message_text
from a2a.server.agent_execution.agent_executor import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue_v2 import EventQueue
from a2a.types.a2a_pb2 import Message, Part, Role
from google.adk.runners import Runner
from google.genai.types import Content
from google.genai.types import Part as GenaiPart

from bayesian_control_tower.agent.bayesian_agent import create_bayesian_agent
from bayesian_control_tower.agent.memory import AgentMemoryService
from bayesian_control_tower.config import settings

logger = structlog.get_logger(__name__)


class BayesianAgentExecutor(AgentExecutor):
    """Runs the Bayesian ADK agent and returns a single A2A Message."""

    def __init__(self) -> None:
        self._memory = AgentMemoryService(app_name=settings.agent_name)
        self._agent = create_bayesian_agent()
        self._runner = Runner(
            agent=self._agent,
            app_name=settings.agent_name,
            session_service=self._memory.session_service,
        )

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        task_id = context.task_id or str(uuid.uuid4())
        context_id = context.context_id or task_id
        user_text = get_message_text(context.message) if context.message else ""

        log = logger.bind(task_id=task_id)
        log.info("bayesian_executor.execute", user_text_len=len(user_text))

        await self._memory.get_or_create_session(user_id=context_id, session_id=task_id)

        response_parts: list[str] = []
        async for event in self._runner.run_async(
            user_id=context_id,
            session_id=task_id,
            new_message=Content(role="user", parts=[GenaiPart(text=user_text)]),
        ):
            if event.is_final_response() and event.content:
                for part in event.content.parts or []:
                    if part.text:
                        response_parts.append(part.text)

        response_text = "\n".join(response_parts) or "(no response)"
        log.info("bayesian_executor.complete", response_len=len(response_text))

        await event_queue.enqueue_event(
            Message(
                message_id=str(uuid.uuid4()),
                role=Role.ROLE_AGENT,
                parts=[Part(text=response_text)],
            )
        )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        # TODO: cancel in-flight ADK runner coroutine
        logger.info("bayesian_executor.cancel", task_id=context.task_id)
