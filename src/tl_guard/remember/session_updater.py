"""Update session memory after each turn."""

from __future__ import annotations

from tl_guard.models import PolicyOutcome, TurnRecord
from tl_guard.perceive.session_state import SessionState, SessionStore


def update_session(
    store: SessionStore,
    state: SessionState,
    turn: TurnRecord,
) -> SessionState:
    state.turns.append(turn)
    state.add_language(turn.detected_language)
    state.last_language = turn.detected_language
    state.last_authorized_tier = turn.authorized_tier
    state.mastery = turn.mastery
    if turn.outcome == PolicyOutcome.REWRITE:
        state.consecutive_rewrites += 1
    else:
        state.consecutive_rewrites = 0
    store.save(state)
    return state
