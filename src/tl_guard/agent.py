"""TL-Guard agent: Perceive → Decide → Act → Reflect → Remember.

TLGuardAgent is a student-facing multilingual buddy. Pedagogical safety is built
into Decide (Scaffold Map + disclosure), Act (context retrieve + constrained
LLM), and Reflect (post-check + audit). The LLM is only a tool used inside Act.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from tl_guard.act.llm_executor import get_llm
from tl_guard.act.retriever import KnowledgeRetriever
from tl_guard.config_loader import ScaffoldMapConfig, load_scaffold_map
from tl_guard.decide.disclosure_checker import check_disclosure
from tl_guard.decide.language_selector import select_response_language
from tl_guard.decide.scaffold_map import ScaffoldMap
from tl_guard.decide.scaffold_selector import select_scaffold_tier
from tl_guard.models import GenerationPlan, LanguageIntent, PolicyOutcome, TurnRecord
from tl_guard.perceive.intent_classifier import classify_intent, similar_question
from tl_guard.perceive.language_detector import detect_language
from tl_guard.perceive.session_state import STORE, SessionState, SessionStore
from tl_guard.pipeline.turn_pipeline import execute_act_reflect
from tl_guard.reflect.escalation import AUDIT_LOG
from tl_guard.remember.session_updater import update_session

if TYPE_CHECKING:
    from tl_guard.act.llm_executor import LLMClient


class TLGuardAgent:
    """Goal-driven multilingual tutoring agent with built-in self-guardrails."""

    def __init__(
        self,
        scaffold_map: ScaffoldMapConfig | None = None,
        constitution: ScaffoldMapConfig | None = None,  # backward-compat
        lsm: ScaffoldMapConfig | None = None,  # backward-compat
        store: SessionStore | None = None,
        llm: LLMClient | None = None,
        retriever: KnowledgeRetriever | None = None,
    ) -> None:
        cfg = scaffold_map or constitution or lsm or load_scaffold_map("python_intro")
        self.scaffold_map = ScaffoldMap(cfg)
        self.constitution = self.scaffold_map  # alias
        self.lsm = cfg  # alias for older call sites
        self.engine = self.scaffold_map.engine
        self.store = store or STORE
        self.llm = llm if llm is not None else get_llm()
        self.retriever = retriever if retriever is not None else KnowledgeRetriever()

    def create_session(self, concept: str = "variables") -> SessionState:
        return self.store.create(course_id=self.scaffold_map.course_id, concept=concept)

    def handle_turn(self, session_id: str, student_message: str) -> TurnRecord:
        """One full agent loop over a student message."""
        state = self.store.get(session_id)
        if state is None:
            raise KeyError(f"Unknown session: {session_id}")
        tracker = self.store.tracker(session_id)
        assert tracker is not None

        # --- Perceive ---
        detection = detect_language(student_message)
        lang = detection.language
        asked_same = any(
            similar_question(student_message, prev) for prev in state.last_student_messages()
        )
        intent_result = classify_intent(
            student_message,
            previous_language=state.last_language,
            current_language=lang,
            mastery=state.mastery,
            asked_same_before=asked_same,
            last_authorized_tier=(
                state.last_authorized_tier.value if state.last_authorized_tier else None
            ),
        )
        correct = tracker.infer_correctness(student_message)
        mastery = tracker.update(correct)

        # --- Decide (Scaffold Map) ---
        esc = self.scaffold_map.escalation
        tighten = intent_result.intent == LanguageIntent.ADVERSARIAL
        if tighten and esc.on_adversarial_intent in {"tighten", "warn"}:
            tighten = True

        tier = select_scaffold_tier(
            self.engine,
            language=lang,
            mastery=mastery,
            intent=intent_result.intent,
            tighten=tighten,
        )
        response_language = select_response_language(
            self.engine,
            student_language=lang,
            scaffold_tier=tier,
            default_language=self.scaffold_map.default_language,
        )
        disclosure = check_disclosure(
            self.engine, language=response_language, tier=tier
        )
        plan = GenerationPlan(
            scaffold_tier=disclosure.tier,
            response_language=disclosure.language,
            authorized=disclosure.authorized,
            intent=intent_result.intent,
            reason=disclosure.reason,
            tighten=tighten,
        )

        if (
            intent_result.intent == LanguageIntent.ADVERSARIAL
            and esc.on_adversarial_intent == "block"
        ):
            plan.authorized = False
            plan.reason = "blocked due to adversarial language-switch intent"

        prior_withheld = any(
            t.outcome in {PolicyOutcome.BLOCK, PolicyOutcome.REWRITE}
            and t.detected_language != lang
            for t in state.turns
        )

        # --- Act + Reflect (context-grounded) ---
        result = execute_act_reflect(
            llm=self.llm,
            plan=plan,
            student_message=student_message,
            course=self.scaffold_map.name,
            concept=state.concept,
            course_id=self.scaffold_map.course_id,
            prior_withheld=prior_withheld,
            on_leakage=esc.on_leakage if esc.on_leakage in {"rewrite", "block"} else "rewrite",
            on_policy_violation=esc.on_policy_violation
            if esc.on_policy_violation in {"rewrite", "block"}
            else "rewrite",
            retriever=self.retriever,
        )

        outcome = result.outcome
        notes = list(intent_result.reasons) + list(result.post_check.reasons)
        if result.context_chunks:
            notes.append(f"context_chunks={len(result.context_chunks)}")

        if intent_result.intent == LanguageIntent.ADVERSARIAL or outcome in {
            PolicyOutcome.ESCALATE,
            PolicyOutcome.BLOCK,
        }:
            AUDIT_LOG.add(
                session_id=session_id,
                turn_index=len(state.turns),
                reason="; ".join(notes) or "self-guardrail event",
                student_message=student_message,
                draft_response=result.raw_llm_text or result.text,
                recommended_action="audit only — agent already self-regulated",
            )
            if outcome == PolicyOutcome.ESCALATE:
                outcome = PolicyOutcome.REWRITE
                notes.append("escalation demoted to rewrite (no teacher workflow)")

        if state.consecutive_rewrites >= 2 and outcome == PolicyOutcome.REWRITE:
            notes.append("consecutive rewrites — audited")
            AUDIT_LOG.add(
                session_id=session_id,
                turn_index=len(state.turns),
                reason="consecutive rewrites",
                student_message=student_message,
                draft_response=result.text,
                recommended_action="audit only",
            )

        turn = TurnRecord(
            turn_index=len(state.turns),
            student_message=student_message,
            detected_language=lang,
            intent=intent_result.intent,
            authorized_tier=plan.scaffold_tier,
            selected_tier=plan.scaffold_tier,
            response_language=plan.response_language,
            assistant_message=result.text,
            outcome=outcome,
            mastery=mastery,
            notes=notes,
            metadata={
                "detection_confidence": detection.confidence,
                "code_mixed": detection.is_code_mixed,
                "intent_confidence": intent_result.confidence,
                "leakage_score": result.post_check.leakage_score,
                "context_sources": [
                    {"source_id": c.source_id, "title": c.title, "score": c.score}
                    for c in result.context_chunks
                ],
            },
        )

        update_session(self.store, state, turn)
        return turn
