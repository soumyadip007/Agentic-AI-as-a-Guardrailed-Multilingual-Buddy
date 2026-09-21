"""Disclosure contract checks before generation."""

from __future__ import annotations

from dataclasses import dataclass

from tl_guard.decide.lsm_engine import LSMEngine
from tl_guard.models import ScaffoldTier


@dataclass
class DisclosureDecision:
    authorized: bool
    tier: ScaffoldTier
    language: str
    reason: str


def check_disclosure(
    engine: LSMEngine,
    *,
    language: str,
    tier: ScaffoldTier,
) -> DisclosureDecision:
    if engine.authorize(language, tier):
        return DisclosureDecision(True, tier, language, "authorized by LSM")

    clamped = engine.clamp(language, tier)
    if engine.authorize(language, clamped):
        return DisclosureDecision(
            True,
            clamped,
            language,
            f"clamped {tier.value} → {clamped.value} for language={language}",
        )

    # Try default English for same tier
    if engine.authorize("en", clamped):
        return DisclosureDecision(
            True,
            clamped,
            "en",
            f"language {language} blocked for {tier.value}; falling back to en/{clamped.value}",
        )

    return DisclosureDecision(
        False,
        ScaffoldTier.T1,
        language,
        f"no authorized disclosure path for {language}/{tier.value}",
    )
