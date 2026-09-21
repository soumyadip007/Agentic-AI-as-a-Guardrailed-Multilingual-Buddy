"""Configuration loading for LSM and escalation policies."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

from tl_guard.models import ScaffoldTier


ROOT = Path(__file__).resolve().parents[2]
CONFIGS_DIR = ROOT / "configs"


class EscalationConfig(BaseModel):
    on_adversarial_intent: str = "escalate"
    on_leakage: str = "rewrite"
    on_policy_violation: str = "rewrite"


class LSMConfig(BaseModel):
    course_id: str
    name: str
    description: str = ""
    default_language: str = "en"
    languages: list[str]
    tiers: list[ScaffoldTier]
    matrix: dict[str, dict[str, bool]]
    topics: list[str] = Field(default_factory=list)
    escalation: EscalationConfig = Field(default_factory=EscalationConfig)

    def max_authorized_tier(self, language: str) -> ScaffoldTier | None:
        lang = language if language in self.matrix else (
            "mixed" if language == "mixed" else self.default_language
        )
        if lang not in self.matrix:
            lang = self.default_language
        row = self.matrix.get(lang, {})
        best: ScaffoldTier | None = None
        for tier in [ScaffoldTier.T1, ScaffoldTier.T2, ScaffoldTier.T3, ScaffoldTier.T4]:
            if row.get(tier.value, False):
                best = tier
        return best

    def is_authorized(self, language: str, tier: ScaffoldTier) -> bool:
        lang = language if language in self.matrix else self.default_language
        if language == "mixed" and "mixed" in self.matrix:
            lang = "mixed"
        return bool(self.matrix.get(lang, {}).get(tier.value, False))


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_lsm(course_id: str | None = None, path: Path | None = None) -> LSMConfig:
    if path is None:
        if course_id is None:
            course_id = "python_intro"
        mapping = {
            "python_intro": "lsm_python_intro.yaml",
            "linear_algebra": "lsm_linear_algebra.yaml",
            "general_science": "lsm_general_science.yaml",
        }
        filename = mapping.get(course_id, f"lsm_{course_id}.yaml")
        path = CONFIGS_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"LSM config not found: {path}")
    data = load_yaml(path)
    return LSMConfig.model_validate(data)


def list_courses() -> list[dict[str, str]]:
    courses = []
    for path in sorted(CONFIGS_DIR.glob("lsm_*.yaml")):
        data = load_yaml(path)
        courses.append(
            {
                "course_id": data.get("course_id", path.stem),
                "name": data.get("name", path.stem),
                "path": str(path),
            }
        )
    return courses


def save_lsm(config: LSMConfig, path: Path | None = None) -> Path:
    if path is None:
        path = CONFIGS_DIR / f"lsm_{config.course_id}.yaml"
    payload = config.model_dump(mode="json")
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(payload, f, sort_keys=False, allow_unicode=True)
    return path
