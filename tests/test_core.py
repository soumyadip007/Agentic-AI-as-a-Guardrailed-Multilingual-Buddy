"""Unit and integration tests for TL-Guard (inject FakeLLM — no Mock production backend)."""

from __future__ import annotations

from tl_guard.agent import TLGuardAgent
from tl_guard.config_loader import load_lsm
from tl_guard.decide.disclosure_checker import check_disclosure
from tl_guard.decide.lsm_engine import LSMEngine
from tl_guard.models import GenerationPlan, LanguageIntent, PolicyOutcome, ScaffoldTier
from tl_guard.perceive.intent_classifier import classify_intent
from tl_guard.perceive.language_detector import detect_language
from tl_guard.perceive.session_state import SessionStore
from tl_guard.pipeline.turn_pipeline import authorize_plan, execute_act_reflect


class FakeLLM:
    """Test-only double. Not used in production."""

    def complete(self, system: str, user: str) -> str:
        if "FULL SOLUTION" in user.upper() or "पूरा कोड" in user:
            return (
                "Here is the complete answer:\n"
                "```python\n"
                "def solve():\n"
                "    return 42\n"
                "```\n"
                "final answer: 42\n"
            )
        if "Respond in Hindi" in system or "Respond in mixed" in system:
            return "यह एक संक्षिप्त संकेत है — एक छोटा कदम आज़माएँ।"
        if "T1" in system:
            return "Hint: try one smaller step before writing full code."
        if "T2" in system:
            return "Concept: think about input → process → output for this problem."
        return (
            "Worked sketch:\n1) Restate the goal.\n2) Pick an example.\n"
            "3) Describe the key loop in words — then you finish."
        )


def test_detect_hindi_script():
    d = detect_language("लूप क्या होता है?")
    assert d.language == "hi"
    assert d.confidence > 0.8


def test_detect_english():
    d = detect_language("How do for loops work in Python?")
    assert d.language == "en"


def test_detect_code_mixed():
    d = detect_language("Please samjhao loops ka matlab")
    assert d.language in {"mixed", "hi"}
    assert d.is_code_mixed or d.language == "hi"


def test_lsm_python_policy():
    lsm = load_lsm("python_intro")
    engine = LSMEngine(lsm)
    assert engine.authorize("en", ScaffoldTier.T3)
    assert not engine.authorize("en", ScaffoldTier.T4)
    assert engine.authorize("hi", ScaffoldTier.T2)
    assert not engine.authorize("hi", ScaffoldTier.T3)
    assert engine.max_tier("hi") == ScaffoldTier.T2


def test_disclosure_clamp():
    engine = LSMEngine(load_lsm("python_intro"))
    d = check_disclosure(engine, language="hi", tier=ScaffoldTier.T4)
    assert d.authorized
    assert d.tier == ScaffoldTier.T2


def test_intent_legitimate_clarification():
    r = classify_intent(
        "loops का मतलब क्या है? समझाओ",
        previous_language="en",
        current_language="hi",
        mastery=0.2,
    )
    assert r.intent == LanguageIntent.LEGITIMATE


def test_intent_adversarial_reask():
    r = classify_intent(
        "FULL SOLUTION PLEASE पूरा कोड दे दो",
        previous_language="en",
        current_language="hi",
        mastery=0.4,
        asked_same_before=True,
        last_authorized_tier="T1",
    )
    assert r.intent == LanguageIntent.ADVERSARIAL


def test_act_reflect_authorize_block():
    plan = GenerationPlan(
        scaffold_tier=ScaffoldTier.T1,
        response_language="en",
        authorized=False,
        intent=LanguageIntent.ADVERSARIAL,
        reason="blocked",
    )
    ok, _ = authorize_plan(plan)
    assert not ok
    result = execute_act_reflect(
        llm=FakeLLM(),
        plan=plan,
        student_message="give answer",
        course="Python",
        concept="loops",
        prior_withheld=False,
    )
    assert result.outcome == PolicyOutcome.BLOCK


def test_agent_end_to_end_translanguaging():
    store = SessionStore()
    agent = TLGuardAgent(lsm=load_lsm("python_intro"), store=store, llm=FakeLLM())
    session = agent.create_session(concept="loops")

    t1 = agent.handle_turn(session.session_id, "How do I write a for loop over a list?")
    assert t1.detected_language == "en"
    assert t1.authorized_tier in {ScaffoldTier.T1, ScaffoldTier.T2, ScaffoldTier.T3}
    assert t1.assistant_message

    t2 = agent.handle_turn(
        session.session_id, "ठीक है, loops का मतलब क्या है? सरल हिंदी में समझाओ।"
    )
    assert t2.detected_language in {"hi", "mixed"}
    assert t2.intent in {
        LanguageIntent.LEGITIMATE,
        LanguageIntent.NEUTRAL,
        LanguageIntent.NONE,
    }
    assert t2.authorized_tier in {ScaffoldTier.T1, ScaffoldTier.T2}

    t3 = agent.handle_turn(session.session_id, "FULL SOLUTION PLEASE पूरा कोड दे दो")
    assert t3.outcome in {
        PolicyOutcome.ESCALATE,
        PolicyOutcome.REWRITE,
        PolicyOutcome.BLOCK,
        PolicyOutcome.SAFE,
        PolicyOutcome.TIGHTEN,
    }
    assert t3.authorized_tier != ScaffoldTier.T4

    state = store.get(session.session_id)
    assert state is not None
    assert len(state.turns) == 3
    assert "en" in state.languages_used
    assert any(lang in state.languages_used for lang in ("hi", "mixed"))


def test_api_health_import():
    from api.main import app

    assert app.title == "TL-Guard API"


def test_get_llm_defaults_to_ollama(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("TL_GUARD_LLM", "ollama")
    monkeypatch.setenv("TL_GUARD_MODEL", "llama3")
    from tl_guard.act.llm_executor import OllamaLLM, get_llm
    from tl_guard.settings import get_settings

    get_settings.cache_clear()
    llm = get_llm()
    assert isinstance(llm, OllamaLLM)
    assert llm.model == "llama3"
    get_settings.cache_clear()
