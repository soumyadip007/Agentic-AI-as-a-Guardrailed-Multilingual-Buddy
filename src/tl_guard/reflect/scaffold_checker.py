"""Scaffold consistency checks."""

from __future__ import annotations

from tl_guard.act.rewriter import looks_like_full_solution
from tl_guard.models import ScaffoldTier


def scaffold_over_discloses(response: str, authorized_tier: ScaffoldTier) -> bool:
    if authorized_tier in {ScaffoldTier.T1, ScaffoldTier.T2}:
        return looks_like_full_solution(response)
    if authorized_tier == ScaffoldTier.T3:
        # Full fenced multi-function dumps are overkill for T3
        return response.count("```") >= 2 and looks_like_full_solution(response)
    return False
