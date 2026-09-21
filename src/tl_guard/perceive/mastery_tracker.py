"""Simple Bayesian Knowledge Tracing for per-concept mastery."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class BKTParams:
    p_l0: float = 0.3  # prior mastery
    p_t: float = 0.15  # learn
    p_g: float = 0.2  # guess
    p_s: float = 0.1  # slip


@dataclass
class MasteryTracker:
    concept: str = "default"
    params: BKTParams = field(default_factory=BKTParams)
    p_known: float = 0.3
    observations: int = 0

    def __post_init__(self) -> None:
        self.p_known = self.params.p_l0

    @property
    def mastery(self) -> float:
        return round(self.p_known, 4)

    def update(self, correct: bool | None) -> float:
        """Update mastery. None = no evidence (e.g. clarification ask)."""
        if correct is None:
            return self.mastery

        self.observations += 1
        p = self.params
        if correct:
            numer = self.p_known * (1 - p.p_s)
            denom = numer + (1 - self.p_known) * p.p_g
        else:
            numer = self.p_known * p.p_s
            denom = numer + (1 - self.p_known) * (1 - p.p_g)
        if denom <= 0:
            posterior = self.p_known
        else:
            posterior = numer / denom
        self.p_known = posterior + (1 - posterior) * p.p_t
        self.p_known = min(0.99, max(0.01, self.p_known))
        return self.mastery

    def infer_correctness(self, student_message: str) -> bool | None:
        """Lightweight heuristic from message content."""
        lower = student_message.lower()
        positive = ["got it", "samajh", "bujhe", "correct", "yes", "right", "thanks", "thank"]
        negative = ["confused", "nahi", "don't understand", "help", "wrong", "stuck", "error"]
        if any(p in lower for p in positive):
            return True
        if any(n in lower for n in negative):
            return False
        if "?" in student_message or lower.startswith(("what", "how", "why", "kya", "kaise")):
            return None
        return None
