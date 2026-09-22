"""Agent Act + Reflect execution path.

After Decide produces a GenerationPlan, this module:
1. authorize_plan — gate Act if the plan is unauthorized
2. Act — retrieve curriculum context, then call the LLM tool
3. Reflect — post-check for leakage / over-disclosure; rewrite or block

This is an internal stage of TLGuardAgent, not a separate product wrapper.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from tl_guard.act.llm_executor import LLMClient, build_system_prompt
from tl_guard.act.refusal_generator import generate_refusal
from tl_guard.act.retriever import ContextChunk, KnowledgeRetriever
from tl_guard.act.rewriter import rewrite_to_tier
from tl_guard.models import GenerationPlan, PolicyOutcome, PostCheckResult, ScaffoldTier
from tl_guard.reflect.post_checker import post_check


@dataclass
class PipelineResult:
    text: str
    outcome: PolicyOutcome
    post_check: PostCheckResult
    raw_llm_text: str
    context_chunks: list[ContextChunk] = field(default_factory=list)


def authorize_plan(plan: GenerationPlan) -> tuple[bool, str]:
    """Act gate: Decide already chose the plan; refuse generation if unauthorized."""
    if not plan.authorized:
        return False, plan.reason or "disclosure not authorized"
    return True, "ok"


# Backward-compatible alias (prefer authorize_plan)
verify = authorize_plan


def _soft_grounding_note(raw: str, chunks: list[ContextChunk]) -> str | None:
    """Heuristic: if context exists but reply is empty of any shared tokens, note it."""
    if not chunks or not raw.strip():
        return None
    from tl_guard.act.retriever import _tokenize

    ctx_tokens: set[str] = set()
    for c in chunks:
        ctx_tokens |= _tokenize(c.text)
    resp_tokens = _tokenize(raw)
    if not ctx_tokens or not resp_tokens:
        return None
    overlap = len(ctx_tokens & resp_tokens)
    if overlap == 0 and len(raw.split()) > 12:
        return "grounding: low lexical overlap with retrieved context"
    return None


def execute_act_reflect(
    *,
    llm: LLMClient,
    plan: GenerationPlan,
    student_message: str,
    course: str,
    concept: str,
    prior_withheld: bool,
    on_leakage: str = "rewrite",
    on_policy_violation: str = "rewrite",
    course_id: str | None = None,
    retriever: KnowledgeRetriever | None = None,
) -> PipelineResult:
    """Run Act (retrieve + LLM) then Reflect (post-check) for one agent turn."""
    ok, reason = authorize_plan(plan)
    if not ok:
        text = generate_refusal(plan.response_language, reason)
        pc = PostCheckResult(ok=False, outcome=PolicyOutcome.BLOCK, reasons=[reason])
        return PipelineResult(
            text=text, outcome=PolicyOutcome.BLOCK, post_check=pc, raw_llm_text=""
        )

    chunks: list[ContextChunk] = []
    if retriever is not None and course_id:
        chunks = retriever.retrieve(
            course_id=course_id,
            concept=concept,
            query=student_message,
            top_k=3,
        )

    system = build_system_prompt(
        tier=plan.scaffold_tier,
        language=plan.response_language,
        course=course,
        concept=concept,
        context_chunks=chunks or None,
    )
    raw = llm.complete(system, student_message)

    pc = post_check(
        raw,
        authorized_tier=plan.scaffold_tier,
        response_language=plan.response_language,
        prior_withheld=prior_withheld,
        on_leakage=on_leakage if on_leakage in {"rewrite", "block", "escalate"} else "rewrite",
    )
    # Map escalate → rewrite (no teacher workflow)
    if pc.outcome == PolicyOutcome.ESCALATE:
        rewritten = rewrite_to_tier(raw, ScaffoldTier.T1, plan.response_language)
        pc = PostCheckResult(
            ok=False,
            outcome=PolicyOutcome.REWRITE,
            leakage_score=pc.leakage_score,
            over_disclosure=pc.over_disclosure,
            reasons=list(pc.reasons) + ["escalation mapped to rewrite (self-guardrail)"],
            rewritten_text=rewritten,
        )

    grounding = _soft_grounding_note(raw, chunks)
    if grounding:
        pc.reasons = list(pc.reasons) + [grounding]

    if pc.outcome == PolicyOutcome.SAFE:
        return PipelineResult(
            text=raw,
            outcome=PolicyOutcome.SAFE,
            post_check=pc,
            raw_llm_text=raw,
            context_chunks=chunks,
        )

    if pc.outcome == PolicyOutcome.REWRITE:
        rewritten = pc.rewritten_text or rewrite_to_tier(
            raw, plan.scaffold_tier, plan.response_language
        )
        return PipelineResult(
            text=rewritten,
            outcome=PolicyOutcome.REWRITE,
            post_check=pc,
            raw_llm_text=raw,
            context_chunks=chunks,
        )

    if pc.outcome == PolicyOutcome.BLOCK:
        return PipelineResult(
            text=generate_refusal(plan.response_language, "; ".join(pc.reasons)),
            outcome=PolicyOutcome.BLOCK,
            post_check=pc,
            raw_llm_text=raw,
            context_chunks=chunks,
        )

    rewritten = rewrite_to_tier(raw, ScaffoldTier.T1, plan.response_language)
    return PipelineResult(
        text=rewritten,
        outcome=PolicyOutcome.REWRITE,
        post_check=pc,
        raw_llm_text=raw,
        context_chunks=chunks,
    )


# Backward-compatible alias (prefer execute_act_reflect)
run_pipeline = execute_act_reflect
