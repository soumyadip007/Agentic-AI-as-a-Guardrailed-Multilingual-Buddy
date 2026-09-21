"""TL-Guard turn pipeline: verify → LLM → post-check → output."""

from __future__ import annotations

from dataclasses import dataclass

from tl_guard.act.llm_executor import LLMClient, build_system_prompt
from tl_guard.act.refusal_generator import generate_refusal
from tl_guard.act.rewriter import rewrite_to_tier
from tl_guard.models import GenerationPlan, PolicyOutcome, PostCheckResult, ScaffoldTier
from tl_guard.reflect.post_checker import post_check


@dataclass
class PipelineResult:
    text: str
    outcome: PolicyOutcome
    post_check: PostCheckResult
    raw_llm_text: str


def verify(plan: GenerationPlan) -> tuple[bool, str]:
    """Layer 1 verification gate."""
    if not plan.authorized:
        return False, plan.reason or "disclosure not authorized"
    return True, "ok"


def run_pipeline(
    *,
    llm: LLMClient,
    plan: GenerationPlan,
    student_message: str,
    course: str,
    concept: str,
    prior_withheld: bool,
    on_leakage: str = "rewrite",
    on_policy_violation: str = "rewrite",
) -> PipelineResult:
    ok, reason = verify(plan)
    if not ok:
        text = generate_refusal(plan.response_language, reason)
        pc = PostCheckResult(ok=False, outcome=PolicyOutcome.BLOCK, reasons=[reason])
        return PipelineResult(text=text, outcome=PolicyOutcome.BLOCK, post_check=pc, raw_llm_text="")

    system = build_system_prompt(
        tier=plan.scaffold_tier,
        language=plan.response_language,
        course=course,
        concept=concept,
    )
    raw = llm.complete(system, student_message)

    pc = post_check(
        raw,
        authorized_tier=plan.scaffold_tier,
        response_language=plan.response_language,
        prior_withheld=prior_withheld,
        on_leakage=on_leakage,
    )

    if pc.outcome == PolicyOutcome.SAFE:
        return PipelineResult(text=raw, outcome=PolicyOutcome.SAFE, post_check=pc, raw_llm_text=raw)

    if pc.outcome == PolicyOutcome.REWRITE:
        rewritten = pc.rewritten_text or rewrite_to_tier(
            raw, plan.scaffold_tier, plan.response_language
        )
        return PipelineResult(
            text=rewritten,
            outcome=PolicyOutcome.REWRITE,
            post_check=pc,
            raw_llm_text=raw,
        )

    if pc.outcome == PolicyOutcome.BLOCK:
        return PipelineResult(
            text=generate_refusal(plan.response_language, "; ".join(pc.reasons)),
            outcome=PolicyOutcome.BLOCK,
            post_check=pc,
            raw_llm_text=raw,
        )

    # escalate — still return a safe rewritten draft for the student while queuing
    rewritten = rewrite_to_tier(raw, ScaffoldTier.T1, plan.response_language)
    return PipelineResult(
        text=rewritten,
        outcome=PolicyOutcome.ESCALATE,
        post_check=pc,
        raw_llm_text=raw,
    )
