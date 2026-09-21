"""Session state for multi-turn tutoring."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from tl_guard.models import ScaffoldTier, TurnRecord
from tl_guard.perceive.mastery_tracker import MasteryTracker


class SessionState(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid4()))
    course_id: str = "python_intro"
    concept: str = "variables"
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    turns: list[TurnRecord] = Field(default_factory=list)
    languages_used: list[str] = Field(default_factory=list)
    mastery: float = 0.3
    last_language: str | None = None
    last_authorized_tier: ScaffoldTier | None = None
    consecutive_rewrites: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = {"arbitrary_types_allowed": True}

    def add_language(self, lang: str) -> None:
        if lang not in self.languages_used:
            self.languages_used.append(lang)

    def last_student_messages(self, n: int = 3) -> list[str]:
        return [t.student_message for t in self.turns[-n:]]


class SessionStore:
    """In-memory session store (swap for DB later)."""

    def __init__(self) -> None:
        self._sessions: dict[str, SessionState] = {}
        self._trackers: dict[str, MasteryTracker] = {}

    def create(self, course_id: str = "python_intro", concept: str = "variables") -> SessionState:
        state = SessionState(course_id=course_id, concept=concept)
        self._sessions[state.session_id] = state
        self._trackers[state.session_id] = MasteryTracker(concept=concept)
        return state

    def get(self, session_id: str) -> SessionState | None:
        return self._sessions.get(session_id)

    def tracker(self, session_id: str) -> MasteryTracker | None:
        return self._trackers.get(session_id)

    def list_sessions(self) -> list[SessionState]:
        return list(self._sessions.values())

    def save(self, state: SessionState) -> None:
        self._sessions[state.session_id] = state


# Process-wide store for API + UI
STORE = SessionStore()
