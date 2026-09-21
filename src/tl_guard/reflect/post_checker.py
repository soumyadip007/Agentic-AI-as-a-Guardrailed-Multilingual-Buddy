"""Multilingual post-check orchestration."""

from __future__ import annotations

from tl_guard.act.rewriter import rewrite_to_tier
from tl_guard.models import PolicyOutcome, PostCheckResult, ScaffoldTier
from tl_guard.reflect.leakage_detector import leakage_score
from tl_guard.reflect.scaffold_checker import scaffold_over_discloses


def post_check(
    response: str,
    *,
    authorized_tier: ScaffoldTier,
    response_language: str,
    prior_withheld: bool,
    on_leakage: str = "rewrite",
) -> PostCheckResult:
    reasons: list[str] = []
    leak = leakage_score(
        response, authorized_tier=authorized_tier, prior_withheld=prior_withheld
    )
    over = scaffold_over_discloses(response, authorized_tier)
    if leak >= 0.5:
        reasons.append(f"cross-lingual/over-disclosure leakage_score={leak:.2f}")
    if over:
        reasons.append("scaffold consistency: response exceeds authorized tier")

    if not reasons:
        return PostCheckResult(ok=True, outcome=PolicyOutcome.SAFE, leakage_score=leak)

    if on_leakage == "block":
        return PostCheckResult(
            ok=False,
            outcome=PolicyOutcome.BLOCK,
            leakage_score=leak,
            over_disclosure=over,
            reasons=reasons,
        )
    if on_leakage == "escalate":
        return PostCheckResult(
            ok=False,
            outcome=PolicyOutcome.ESCALATE,
            leakage_score=leak,
            over_disclosure=over,
            reasons=reasons,
        )

    rewritten = rewrite_to_tier(response, authorized_tier, response_language)
    return PostCheckResult(
        ok=False,
        outcome=PolicyOutcome.REWRITE,
        leakage_score=leak,
        over_disclosure=over,
        reasons=reasons,
        rewritten_text=rewritten,
    )
