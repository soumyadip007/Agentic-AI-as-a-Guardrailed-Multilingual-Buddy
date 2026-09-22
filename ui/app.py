"""Streamlit student buddy UI for TL-Guard (no teacher console)."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from tl_guard.agent import TLGuardAgent  # noqa: E402
from tl_guard.config_loader import list_courses, load_scaffold_map  # noqa: E402
from tl_guard.perceive.session_state import STORE  # noqa: E402

st.set_page_config(page_title="TL-Guard Buddy", page_icon="🧭", layout="wide")


def get_agent(course_id: str) -> TLGuardAgent:
    key = f"agent_{course_id}"
    if key not in st.session_state:
        st.session_state[key] = TLGuardAgent(
            scaffold_map=load_scaffold_map(course_id), store=STORE
        )
    return st.session_state[key]


def student_view() -> None:
    st.header("Multilingual Buddy")
    st.caption(
        "Mix languages freely. TL-Guard self-regulates help level under a fixed "
        "Scaffold Map and grounds answers in local curriculum context."
    )

    courses = list_courses()
    course_id = st.selectbox(
        "Course",
        options=[c["course_id"] for c in courses],
        format_func=lambda cid: next(c["name"] for c in courses if c["course_id"] == cid),
    )
    agent_preview = get_agent(course_id)
    topics = agent_preview.scaffold_map.topics or ["variables"]
    concept = st.selectbox("Concept", options=topics, index=0)

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
                sources = (turn.metadata or {}).get("context_sources") or []
                if sources:
                    with st.expander("Sources used"):
                        for s in sources:
                            st.caption(
                                f"• {s.get('source_id', '?')} "
                                f"({s.get('title', '')}) · score={s.get('score', 0)}"
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
        st.write("Concept:", state.concept)
        if state.turns:
            last = state.turns[-1]
            st.write("Last outcome:", last.outcome.value)
            if last.notes:
                st.write("Notes:")
                for n in last.notes:
                    st.caption(f"• {n}")


def main() -> None:
    st.title("TL-Guard")
    st.markdown(
        "Agentic multilingual buddy · **Perceive → Decide → Act → Reflect → Remember**"
    )
    st.sidebar.markdown("### Buddy")
    st.sidebar.caption(
        "Fixed Scaffold Map · context-grounded Act · "
        "LLM via Ollama (`TL_GUARD_MODEL`) or OpenAI (`TL_GUARD_LLM=openai`)."
    )
    student_view()


if __name__ == "__main__":
    main()
