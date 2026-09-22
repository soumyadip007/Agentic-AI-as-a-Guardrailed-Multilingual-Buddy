"""Scaffold Map authorization engine (language × scaffold tier)."""

from __future__ import annotations

from tl_guard.config_loader import ScaffoldMapConfig
from tl_guard.models import ScaffoldTier, TIER_ORDER, TIER_RANK


class LSMEngine:
    """Clamp/authorize scaffold tiers per language under a frozen Scaffold Map."""

    def __init__(self, config: ScaffoldMapConfig) -> None:
        self.config = config

    def max_tier(self, language: str) -> ScaffoldTier:
        tier = self.config.max_authorized_tier(language)
        if tier is None:
            # Never leave the agent without a response path — allow T1 in default lang
            return ScaffoldTier.T1
        return tier

    def authorize(self, language: str, tier: ScaffoldTier) -> bool:
        return self.config.is_authorized(language, tier)

    def clamp(self, language: str, desired: ScaffoldTier) -> ScaffoldTier:
        max_allowed = self.max_tier(language)
        if TIER_RANK[desired] <= TIER_RANK[max_allowed]:
            return desired
        return max_allowed

    def drop_one(self, tier: ScaffoldTier) -> ScaffoldTier:
        idx = max(0, TIER_RANK[tier] - 1)
        return TIER_ORDER[idx]
