"""FastAPI application for TL-Guard (student buddy + read-only Scaffold Map)."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from tl_guard.agent import TLGuardAgent
from tl_guard.config_loader import ScaffoldMapConfig, list_courses, load_scaffold_map
from tl_guard.models import EscalationItem, TurnRecord
from tl_guard.perceive.session_state import STORE, SessionState
from tl_guard.reflect.escalation import AUDIT_LOG

app = FastAPI(title="TL-Guard API", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_agents: dict[str, TLGuardAgent] = {}


def get_agent(course_id: str = "python_intro") -> TLGuardAgent:
    if course_id not in _agents:
        _agents[course_id] = TLGuardAgent(
            scaffold_map=load_scaffold_map(course_id), store=STORE
        )
    return _agents[course_id]


class CreateSessionRequest(BaseModel):
    course_id: str = "python_intro"
    concept: str = "variables"


class TurnRequest(BaseModel):
    message: str = Field(min_length=1)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/courses")
def courses() -> list[dict[str, str]]:
    return list_courses()


@app.post("/sessions", response_model=SessionState)
def create_session(body: CreateSessionRequest) -> SessionState:
    agent = get_agent(body.course_id)
    return agent.create_session(concept=body.concept)


@app.get("/sessions/{session_id}", response_model=SessionState)
def get_session(session_id: str) -> SessionState:
    state = STORE.get(session_id)
    if not state:
        raise HTTPException(404, "Session not found")
    return state


@app.post("/sessions/{session_id}/turns", response_model=TurnRecord)
def post_turn(session_id: str, body: TurnRequest) -> TurnRecord:
    state = STORE.get(session_id)
    if not state:
        raise HTTPException(404, "Session not found")
    agent = get_agent(state.course_id)
    try:
        return agent.handle_turn(session_id, body.message)
    except KeyError as e:
        raise HTTPException(404, str(e)) from e


@app.get("/scaffold-maps/{course_id}", response_model=ScaffoldMapConfig)
def get_scaffold_map(course_id: str) -> ScaffoldMapConfig:
    """Read-only Scaffold Map (not teacher-editable)."""
    try:
        return load_scaffold_map(course_id)
    except FileNotFoundError as e:
        raise HTTPException(404, str(e)) from e


@app.get("/policies/{course_id}", response_model=ScaffoldMapConfig)
def get_policy(course_id: str) -> ScaffoldMapConfig:
    """Backward-compatible read-only alias for Scaffold Map."""
    return get_scaffold_map(course_id)


@app.get("/audit", response_model=list[EscalationItem])
def list_audit(open_only: bool = False) -> list[EscalationItem]:
    """Research/debug audit log of self-guardrail events."""
    return AUDIT_LOG.list_open() if open_only else AUDIT_LOG.list_all()


@app.get("/escalations", response_model=list[EscalationItem])
def list_escalations(open_only: bool = False) -> list[EscalationItem]:
    return list_audit(open_only=open_only)
