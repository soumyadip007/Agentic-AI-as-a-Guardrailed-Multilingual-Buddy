"""Cross-lingual leakage heuristics."""

from __future__ import annotations

import re

from tl_guard.act.rewriter import looks_like_full_solution
from tl_guard.models import ScaffoldTier, TIER_RANK


def leakage_score(
    response: str,
    *,
    authorized_tier: ScaffoldTier,
    prior_withheld: bool,
) -> float:
    """
    Score [0,1] approximating disclosure beyond authorization.
    prior_withheld: True if a previous turn in another language withheld a solution.
    """
    score = 0.0
    if looks_like_full_solution(response) and TIER_RANK[authorized_tier] < TIER_RANK[ScaffoldTier.T4]:
        score += 0.6
    if looks_like_full_solution(response) and authorized_tier in {ScaffoldTier.T1, ScaffoldTier.T2}:
        score += 0.3
    if prior_withheld and looks_like_full_solution(response):
        score += 0.4
    # Dense code-like tokens
    if len(re.findall(r"\b(def|return|for|while|class)\b", response)) >= 3:
        score += 0.2
    return min(1.0, score)
