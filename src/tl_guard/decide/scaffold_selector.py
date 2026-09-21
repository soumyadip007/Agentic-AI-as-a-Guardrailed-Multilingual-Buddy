"""Select scaffold tier from mastery + LSM constraints."""

from __future__ import annotations

from tl_guard.decide.lsm_engine import LSMEngine
from tl_guard.models import LanguageIntent, ScaffoldTier


def select_scaffold_tier(
    engine: LSMEngine,
    *,
    language: str,
    mastery: float,
    intent: LanguageIntent,
    tighten: bool = False,
) -> ScaffoldTier:
    """
    Mastery-aware tier selection:
    - Low mastery → more support (higher tier) but still LSM-clamped
    - High mastery → lighter hints
    - Adversarial → force down toward T1
    """
    if intent == LanguageIntent.ADVERSARIAL or tighten:
        desired = ScaffoldTier.T1
    elif mastery < 0.35:
        desired = ScaffoldTier.T3
    elif mastery < 0.65:
        desired = ScaffoldTier.T2
    else:
        desired = ScaffoldTier.T1

    return engine.clamp(language, desired)
