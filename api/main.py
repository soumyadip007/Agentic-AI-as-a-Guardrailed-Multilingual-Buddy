"""FastAPI application for TL-Guard."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from tl_guard.agent import TLGuardAgent
from tl_guard.config_loader import LSMConfig, list_courses, load_lsm, save_lsm
from tl_guard.decide.lsm_engine import LSMEngine
from tl_guard.models import EscalationItem, TurnRecord
from tl_guard.perceive.session_state import STORE, SessionState
from tl_guard.reflect.escalation import ESCALATIONS

app = FastAPI(title="TL-Guard API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Agents keyed by course_id
_agents: dict[str, TLGuardAgent] = {}


def get_agent(course_id: str = "python_intro") -> TLGuardAgent:
    if course_id not in _agents:
        _agents[course_id] = TLGuardAgent(lsm=load_lsm(course_id), store=STORE)
    return _agents[course_id]


class CreateSessionRequest(BaseModel):
    course_id: str = "python_intro"
    concept: str = "variables"


class TurnRequest(BaseModel):
    message: str = Field(min_length=1)


class ResolveEscalationRequest(BaseModel):
    note: str = ""


class LSMUpdateRequest(BaseModel):
    config: LSMConfig


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/courses")
def courses() -> list[dict[str, str]]:
    return list_courses()


@app.post("/sessions", response_model=SessionState)
def create_session(body: CreateSessionRequest) -> SessionState:
    agent = get_agent(body.course_id)
    # Refresh LSM in case teacher edited it
    agent.lsm = load_lsm(body.course_id)
    agent.engine = LSMEngine(agent.lsm)
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
    agent.lsm = load_lsm(state.course_id)
    agent.engine = LSMEngine(agent.lsm)
    try:
        return agent.handle_turn(session_id, body.message)
    except KeyError as e:
        raise HTTPException(404, str(e)) from e


@app.get("/policies/{course_id}", response_model=LSMConfig)
def get_policy(course_id: str) -> LSMConfig:
    try:
        return load_lsm(course_id)
    except FileNotFoundError as e:
        raise HTTPException(404, str(e)) from e


@app.put("/policies/{course_id}", response_model=LSMConfig)
def put_policy(course_id: str, body: LSMUpdateRequest) -> LSMConfig:
    cfg = body.config
    cfg.course_id = course_id
    save_lsm(cfg)
    _agents.pop(course_id, None)
    return cfg


@app.get("/escalations", response_model=list[EscalationItem])
def list_escalations(open_only: bool = True) -> list[EscalationItem]:
    return ESCALATIONS.list_open() if open_only else ESCALATIONS.list_all()


@app.post("/escalations/{item_id}/resolve", response_model=EscalationItem)
def resolve_escalation(item_id: str, body: ResolveEscalationRequest) -> EscalationItem:
    item = ESCALATIONS.resolve(item_id, body.note)
    if not item:
        raise HTTPException(404, "Escalation not found")
    return item
