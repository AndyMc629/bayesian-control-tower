"""Agentic memory stub wrapping ADK's InMemorySessionService.

This is the simplest possible setup — session state lives in-process and is
lost on restart. Swap the backing service here when you're ready to persist.

TODO: Replace InMemorySessionService with VertexAI / Firestore / Redis backend.
TODO: Add MemoryService for cross-session recall once ADK memory API stabilises.
"""

from google.adk.sessions import InMemorySessionService, Session


class AgentMemoryService:
    """Thin wrapper around ADK session management."""

    def __init__(self, app_name: str = "bayesian-control-tower") -> None:
        self.app_name = app_name
        self._sessions = InMemorySessionService()

    async def get_or_create_session(self, user_id: str, session_id: str) -> Session:
        existing = await self._sessions.get_session(
            app_name=self.app_name,
            user_id=user_id,
            session_id=session_id,
        )
        if existing:
            return existing

        return await self._sessions.create_session(
            app_name=self.app_name,
            user_id=user_id,
            session_id=session_id,
        )

    @property
    def session_service(self) -> InMemorySessionService:
        return self._sessions
