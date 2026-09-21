"""TL-Guard agent: Perceive → Decide → Act → Reflect → Remember."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tl_guard.act.llm_executor import get_llm
from tl_guard.config_loader import LSMConfig, load_lsm
from tl_guard.decide.disclosure_checker import check_disclosure
from tl_guard.decide.language_selector import select_response_language
from tl_guard.decide.lsm_engine import LSMEngine
from tl_guard.decide.scaffold_selector import select_scaffold_tier
from tl_guard.models import GenerationPlan, LanguageIntent, PolicyOutcome, TurnRecord
from tl_guard.perceive.intent_classifier import classify_intent, similar_question
from tl_guard.perceive.language_detector import detect_language
from tl_guard.perceive.session_state import STORE, SessionState, SessionStore
from tl_guard.pipeline.turn_pipeline import run_pipeline
from tl_guard.reflect.escalation import ESCALATIONS
from tl_guard.remember.session_updater import update_session

if TYPE_CHECKING:
    from tl_guard.act.llm_executor import LLMClient


class TLGuardAgent:
    def __init__(
        self,
        lsm: LSMConfig | None = None,
        store: SessionStore | None = None,
        llm: LLMClient | None = None,
    ) -> None:
        self.lsm = lsm or load_lsm("python_intro")
        self.engine = LSMEngine(self.lsm)
        self.store = store or STORE
        self.llm = llm if llm is not None else get_llm()

    def create_session(self, concept: str = "variables") -> SessionState:
        return self.store.create(course_id=self.lsm.course_id, concept=concept)

    def handle_turn(self, session_id: str, student_message: str) -> TurnRecord:
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

        # --- Decide ---
        tighten = intent_result.intent == LanguageIntent.ADVERSARIAL
        if tighten and self.lsm.escalation.on_adversarial_intent == "tighten":
            tighten = True

        desired_lang_for_policy = lang
        tier = select_scaffold_tier(
            self.engine,
            language=desired_lang_for_policy,
            mastery=mastery,
            intent=intent_result.intent,
            tighten=tighten,
        )
        response_language = select_response_language(
            self.engine,
            student_language=lang,
            scaffold_tier=tier,
            default_language=self.lsm.default_language,
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

        # Adversarial with escalate policy → authorize T1 but escalate after
        force_escalate = (
            intent_result.intent == LanguageIntent.ADVERSARIAL
            and self.lsm.escalation.on_adversarial_intent == "escalate"
        )
        if (
            intent_result.intent == LanguageIntent.ADVERSARIAL
            and self.lsm.escalation.on_adversarial_intent == "block"
        ):
            plan.authorized = False
            plan.reason = "blocked due to adversarial language-switch intent"

        prior_withheld = any(
            t.outcome in {PolicyOutcome.BLOCK, PolicyOutcome.REWRITE}
            and t.detected_language != lang
            for t in state.turns
        )

        # --- Act + Reflect (pipeline) ---
        result = run_pipeline(
            llm=self.llm,
            plan=plan,
            student_message=student_message,
            course=self.lsm.name,
            concept=state.concept,
            prior_withheld=prior_withheld,
            on_leakage=self.lsm.escalation.on_leakage,
            on_policy_violation=self.lsm.escalation.on_policy_violation,
        )

        outcome = result.outcome
        notes = list(intent_result.reasons) + list(result.post_check.reasons)
        if force_escalate and outcome != PolicyOutcome.BLOCK:
            outcome = PolicyOutcome.ESCALATE
            notes.append("adversarial intent → teacher escalation")
            ESCALATIONS.add(
                session_id=session_id,
                turn_index=len(state.turns),
                reason="; ".join(notes),
                student_message=student_message,
                draft_response=result.raw_llm_text or result.text,
                recommended_action="review and confirm scaffold tier",
            )
        elif outcome == PolicyOutcome.ESCALATE:
            ESCALATIONS.add(
                session_id=session_id,
                turn_index=len(state.turns),
                reason="; ".join(result.post_check.reasons) or "post-check escalate",
                student_message=student_message,
                draft_response=result.raw_llm_text or result.text,
                recommended_action="rewrite or approve",
            )

        if state.consecutive_rewrites >= 2 and outcome == PolicyOutcome.REWRITE:
            outcome = PolicyOutcome.ESCALATE
            notes.append("auto-escalate after consecutive rewrites")
            ESCALATIONS.add(
                session_id=session_id,
                turn_index=len(state.turns),
                reason="consecutive rewrites",
                student_message=student_message,
                draft_response=result.text,
                recommended_action="teacher review",
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
            },
        )

        # --- Remember ---
        update_session(self.store, state, turn)
        return turn
