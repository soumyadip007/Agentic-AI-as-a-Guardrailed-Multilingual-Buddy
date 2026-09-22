"""Scaffold Map: frozen pedagogical self-guardrails (not teacher-editable).

The Scaffold Map is a fixed language×scaffold authorization table plus
adversarial/leakage response rules. It is loaded once per course and never
mutated at runtime by a teacher console.
"""

from __future__ import annotations

from tl_guard.config_loader import ScaffoldMapConfig, load_scaffold_map
from tl_guard.decide.lsm_engine import LSMEngine
from tl_guard.models import ScaffoldTier


class ScaffoldMap:
    """Frozen self-guardrail engine used in Decide."""

    def __init__(
        self,
        config: ScaffoldMapConfig | None = None,
        course_id: str = "python_intro",
    ) -> None:
        self.config = config or load_scaffold_map(course_id)
        self._engine = LSMEngine(self.config)

    @property
    def course_id(self) -> str:
        return self.config.course_id

    @property
    def name(self) -> str:
        return self.config.name

    @property
    def default_language(self) -> str:
        return self.config.default_language

    @property
    def topics(self) -> list[str]:
        return list(self.config.topics)

    @property
    def escalation(self):
        return self.config.escalation

    @property
    def engine(self) -> LSMEngine:
        return self._engine

    def max_tier(self, language: str) -> ScaffoldTier:
        return self._engine.max_tier(language)

    def authorize(self, language: str, tier: ScaffoldTier) -> bool:
        return self._engine.authorize(language, tier)

    def clamp(self, language: str, desired: ScaffoldTier) -> ScaffoldTier:
        return self._engine.clamp(language, desired)

    def drop_one(self, tier: ScaffoldTier) -> ScaffoldTier:
        return self._engine.drop_one(tier)


# Backward-compatible alias
BuddyConstitution = ScaffoldMap
