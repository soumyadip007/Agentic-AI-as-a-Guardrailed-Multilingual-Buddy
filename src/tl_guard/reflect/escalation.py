"""Research/debug audit log (replaces teacher escalation queue).

Violations and adversarial turns are recorded for analysis. There is no
teacher workflow — the agent self-regulates via Scaffold Map + Reflect.
"""

from __future__ import annotations

from uuid import uuid4

from tl_guard.models import EscalationItem


class AuditLog:
    """In-memory audit trail of self-guardrail events."""

    def __init__(self) -> None:
        self._items: dict[str, EscalationItem] = {}

    def add(
        self,
        *,
        session_id: str,
        turn_index: int,
        reason: str,
        student_message: str,
        draft_response: str,
        recommended_action: str,
    ) -> EscalationItem:
        item = EscalationItem(
            id=str(uuid4()),
            session_id=session_id,
            turn_index=turn_index,
            reason=reason,
            student_message=student_message,
            draft_response=draft_response,
            recommended_action=recommended_action,
        )
        self._items[item.id] = item
        return item

    def list_open(self) -> list[EscalationItem]:
        return [i for i in self._items.values() if not i.resolved]

    def list_all(self) -> list[EscalationItem]:
        return list(self._items.values())

    def resolve(self, item_id: str, note: str = "") -> EscalationItem | None:
        item = self._items.get(item_id)
        if not item:
            return None
        item.resolved = True
        item.resolution_note = note
        return item


# Module-level singleton
AUDIT_LOG = AuditLog()

# Backward-compatible aliases
EscalationQueue = AuditLog
ESCALATIONS = AUDIT_LOG
