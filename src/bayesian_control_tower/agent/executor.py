"""A2A AgentExecutor bridging the a2a-sdk protocol to the ADK Bayesian agent.

Uses the a2a-sdk 1.1.0 API directly (the ADK built-in A2A executor targets an
older SDK version and is not compatible with 1.1.x).
"""

import structlog
from a2a.helpers.proto_helpers import get_message_text
from a2a.server.agent_execution.agent_executor import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue_v2 import EventQueue
from a2a.server.tasks.task_updater import TaskUpdater
from a2a.types.a2a_pb2 import Part
from google.adk.runners import Runner
from google.genai.types import Content
from google.genai.types import Part as GenaiPart

from bayesian_control_tower.agent.bayesian_agent import create_bayesian_agent
from bayesian_control_tower.agent.memory import AgentMemoryService
from bayesian_control_tower.config import settings

logger = structlog.get_logger(__name__)


class BayesianAgentExecutor(AgentExecutor):
    """Executes Bayesian advisory requests via the ADK runner."""

    def __init__(self) -> None:
        self._memory = AgentMemoryService(app_name=settings.agent_name)
        self._agent = create_bayesian_agent()
        self._runner = Runner(
            agent=self._agent,
            app_name=settings.agent_name,
            session_service=self._memory.session_service,
        )

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        task_id = context.task_id or "task-default"
        context_id = context.context_id or task_id

        updater = TaskUpdater(
            event_queue=event_queue,
            task_id=task_id,
            context_id=context_id,
        )
        await updater.start_work()

        log = logger.bind(task_id=task_id, context_id=context_id)
        log.info("bayesian_executor.execute")

        user_text = get_message_text(context.message) if context.message else ""

        await self._memory.get_or_create_session(
            user_id=context_id,
            session_id=task_id,
        )

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

        full_response = "\n".join(response_parts) or "No response generated."
        log.info("bayesian_executor.complete", response_length=len(full_response))

        await updater.add_artifact(parts=[Part(text=full_response)])
        await updater.complete()

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        # TODO: propagate cancellation to the in-flight ADK runner coroutine
        logger.info("bayesian_executor.cancel", task_id=context.task_id)
