"""Shared types and enums for TL-Guard."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ScaffoldTier(str, Enum):
    T1 = "T1"  # nudge / hint
    T2 = "T2"  # conceptual explanation
    T3 = "T3"  # worked example
    T4 = "T4"  # full solution


TIER_ORDER = [ScaffoldTier.T1, ScaffoldTier.T2, ScaffoldTier.T3, ScaffoldTier.T4]
TIER_RANK = {t: i for i, t in enumerate(TIER_ORDER)}


class LanguageIntent(str, Enum):
    LEGITIMATE = "legitimate"
    ADVERSARIAL = "adversarial"
    NEUTRAL = "neutral"
    NONE = "none"  # no language switch


class PolicyOutcome(str, Enum):
    SAFE = "safe"
    REWRITE = "rewrite"
    ESCALATE = "escalate"
    BLOCK = "block"
    TIGHTEN = "tighten"


class TurnRecord(BaseModel):
    turn_index: int
    student_message: str
    detected_language: str
    intent: LanguageIntent
    authorized_tier: ScaffoldTier
    selected_tier: ScaffoldTier
    response_language: str
    assistant_message: str
    outcome: PolicyOutcome
    mastery: float
    notes: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class EscalationItem(BaseModel):
    id: str
    session_id: str
    turn_index: int
    reason: str
    student_message: str
    draft_response: str
    recommended_action: str
    resolved: bool = False
    resolution_note: str | None = None


class GenerationPlan(BaseModel):
    scaffold_tier: ScaffoldTier
    response_language: str
    authorized: bool
    intent: LanguageIntent
    reason: str = ""
    tighten: bool = False


class PostCheckResult(BaseModel):
    ok: bool
    outcome: PolicyOutcome
    leakage_score: float = 0.0
    over_disclosure: bool = False
    reasons: list[str] = Field(default_factory=list)
    rewritten_text: str | None = None
