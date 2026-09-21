"""Streamlit student + teacher UI for TL-Guard."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st
import yaml

# Ensure src is importable when launched via `streamlit run`
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from tl_guard.agent import TLGuardAgent  # noqa: E402
from tl_guard.config_loader import LSMConfig, list_courses, load_lsm, save_lsm  # noqa: E402
from tl_guard.decide.lsm_engine import LSMEngine  # noqa: E402
from tl_guard.perceive.session_state import STORE  # noqa: E402
from tl_guard.reflect.escalation import ESCALATIONS  # noqa: E402

st.set_page_config(page_title="TL-Guard", page_icon="🧭", layout="wide")


def get_agent(course_id: str) -> TLGuardAgent:
    key = f"agent_{course_id}"
    if key not in st.session_state:
        st.session_state[key] = TLGuardAgent(lsm=load_lsm(course_id), store=STORE)
    else:
        # refresh policy
        agent: TLGuardAgent = st.session_state[key]
        agent.lsm = load_lsm(course_id)
        agent.engine = LSMEngine(agent.lsm)
    return st.session_state[key]


def student_view() -> None:
    st.header("Student Buddy")
    st.caption("Mix languages freely. TL-Guard decides help level under teacher policy.")

    courses = list_courses()
    course_id = st.selectbox(
        "Course",
        options=[c["course_id"] for c in courses],
        format_func=lambda cid: next(c["name"] for c in courses if c["course_id"] == cid),
    )
    concept = st.text_input("Concept", value="variables")

    if "chat_session_id" not in st.session_state:
        st.session_state.chat_session_id = None
        st.session_state.chat_course = None

    cols = st.columns([1, 1, 2])
    with cols[0]:
        if st.button("Start new session", type="primary"):
            agent = get_agent(course_id)
            state = agent.create_session(concept=concept)
            st.session_state.chat_session_id = state.session_id
            st.session_state.chat_course = course_id
            st.rerun()
    with cols[1]:
        if st.session_state.chat_session_id:
            st.success(f"Session: {st.session_state.chat_session_id[:8]}…")

    sid = st.session_state.chat_session_id
    if not sid:
        st.info("Start a session to begin tutoring.")
        return

    state = STORE.get(sid)
    if not state:
        st.warning("Session missing — start a new one.")
        return

    left, right = st.columns([2, 1])
    with left:
        for turn in state.turns:
            with st.chat_message("user"):
                st.write(turn.student_message)
                st.caption(f"detected: {turn.detected_language} · intent: {turn.intent.value}")
            with st.chat_message("assistant"):
                st.write(turn.assistant_message)
                st.caption(
                    f"tier {turn.authorized_tier.value} · lang {turn.response_language} · "
                    f"outcome {turn.outcome.value}"
                )

        prompt = st.chat_input("Ask in English, Hindi, Bengali, Spanish, or mixed…")
        if prompt:
            agent = get_agent(state.course_id)
            agent.handle_turn(sid, prompt)
            st.rerun()

    with right:
        st.subheader("Session panel")
        st.metric("Mastery", f"{state.mastery:.0%}")
        st.write("Languages used:", ", ".join(state.languages_used) or "—")
        st.write("Turns:", len(state.turns))
        if state.turns:
            last = state.turns[-1]
            st.write("Last outcome:", last.outcome.value)
            if last.notes:
                st.write("Notes:")
                for n in last.notes:
                    st.caption(f"• {n}")


def teacher_view() -> None:
    st.header("Teacher Console")
    tab_policy, tab_esc = st.tabs(["LSM Editor", "Escalations"])

    with tab_policy:
        courses = list_courses()
        course_id = st.selectbox(
            "Edit course policy",
            options=[c["course_id"] for c in courses],
            key="teacher_course",
        )
        cfg = load_lsm(course_id)
        st.write(cfg.description)

        st.subheader("Language–Scaffold Matrix")
        languages = cfg.languages
        tiers = [t.value if hasattr(t, "value") else t for t in cfg.tiers]

        # Editable matrix via checkboxes
        new_matrix = {}
        for lang in languages:
            st.markdown(f"**{lang}**")
            cols = st.columns(len(tiers))
            row = {}
            for i, tier in enumerate(tiers):
                current = cfg.matrix.get(lang, {}).get(tier, False)
                row[tier] = cols[i].checkbox(
                    tier, value=current, key=f"m_{course_id}_{lang}_{tier}"
                )
            new_matrix[lang] = row

        esc_adv = st.selectbox(
            "On adversarial intent",
            ["warn", "tighten", "escalate", "block"],
            index=["warn", "tighten", "escalate", "block"].index(
                cfg.escalation.on_adversarial_intent
            ),
        )
        esc_leak = st.selectbox(
            "On leakage",
            ["rewrite", "escalate", "block"],
            index=["rewrite", "escalate", "block"].index(cfg.escalation.on_leakage),
        )

        yaml_text = st.text_area(
            "YAML (advanced)",
            value=yaml.safe_dump(cfg.model_dump(mode="json"), sort_keys=False, allow_unicode=True),
            height=220,
        )

        c1, c2 = st.columns(2)
        with c1:
            if st.button("Save matrix from checkboxes", type="primary"):
                cfg.matrix = new_matrix
                cfg.escalation.on_adversarial_intent = esc_adv
                cfg.escalation.on_leakage = esc_leak
                save_lsm(cfg)
                st.success("Policy saved.")
                st.session_state.pop(f"agent_{course_id}", None)
        with c2:
            if st.button("Save from YAML"):
                data = yaml.safe_load(yaml_text)
                parsed = LSMConfig.model_validate(data)
                parsed.course_id = course_id
                save_lsm(parsed)
                st.success("YAML policy saved.")
                st.session_state.pop(f"agent_{course_id}", None)

        # Preview
        st.subheader("Preview")
        lang = st.selectbox("Preview language", languages, key="preview_lang")
        engine = LSMEngine(load_lsm(course_id))
        st.info(f"Max authorized tier for `{lang}`: **{engine.max_tier(lang).value}**")

    with tab_esc:
        open_only = st.checkbox("Open only", value=True)
        items = ESCALATIONS.list_open() if open_only else ESCALATIONS.list_all()
        if not items:
            st.write("No escalations.")
        for item in items:
            with st.expander(
                f"{'✅' if item.resolved else '⚠️'} {item.id[:8]} · session {item.session_id[:8]} · turn {item.turn_index}"
            ):
                st.write("**Reason:**", item.reason)
                st.write("**Student:**", item.student_message)
                st.write("**Draft:**", item.draft_response)
                st.write("**Recommended:**", item.recommended_action)
                note = st.text_input("Resolution note", key=f"note_{item.id}")
                if not item.resolved and st.button("Resolve", key=f"res_{item.id}"):
                    ESCALATIONS.resolve(item.id, note)
                    st.rerun()


def main() -> None:
    st.title("TL-Guard")
    st.markdown(
        "Agentic multilingual buddy · **Perceive → Decide → Act → Reflect → Remember**"
    )
    role = st.sidebar.radio("Role", ["Student", "Teacher"], index=0)
    st.sidebar.markdown("---")
    st.sidebar.caption(
        "LLM: Ollama by default (`TL_GUARD_MODEL`, e.g. llama3). "
        "Optional OpenAI via `TL_GUARD_LLM=openai`."
    )
    if role == "Student":
        student_view()
    else:
        teacher_view()


if __name__ == "__main__":
    main()
