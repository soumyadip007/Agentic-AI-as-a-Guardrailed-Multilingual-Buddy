"""Choose response language under LSM constraints."""

from __future__ import annotations

from tl_guard.decide.lsm_engine import LSMEngine
from tl_guard.models import ScaffoldTier


def select_response_language(
    engine: LSMEngine,
    *,
    student_language: str,
    scaffold_tier: ScaffoldTier,
    default_language: str = "en",
) -> str:
    """Prefer matching the student; fall back if that language cannot host the tier."""
    candidates = []
    if student_language == "mixed":
        candidates = ["mixed", "hi", "bn", "en", default_language]
    else:
        candidates = [student_language, default_language, "en"]

    seen: set[str] = set()
    for lang in candidates:
        if lang in seen:
            continue
        seen.add(lang)
        if engine.authorize(lang, scaffold_tier):
            return lang
        # If exact tier not allowed, still respond in student language at clamped tier
        if engine.max_tier(lang) is not None:
            return lang
    return default_language
