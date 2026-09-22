"""Configuration loading for Scaffold Map (frozen pedagogical self-guardrails)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

from tl_guard.models import ScaffoldTier


ROOT = Path(__file__).resolve().parents[2]
CONFIGS_DIR = ROOT / "configs"


class EscalationConfig(BaseModel):
    """Fixed response rules under the Scaffold Map (no teacher workflow)."""

    on_adversarial_intent: str = "tighten"  # tighten | block | warn
    on_leakage: str = "rewrite"  # rewrite | block
    on_policy_violation: str = "rewrite"


class ScaffoldMapConfig(BaseModel):
    """Frozen language×scaffold map and safety rules for a course."""

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


# Backward-compatible aliases
BuddyConstitutionConfig = ScaffoldMapConfig
LSMConfig = ScaffoldMapConfig


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _scaffold_map_path(course_id: str) -> Path:
    """Resolve Scaffold Map YAML, falling back to legacy filenames."""
    for prefix in ("scaffold_map_", "constitution_", "lsm_"):
        path = CONFIGS_DIR / f"{prefix}{course_id}.yaml"
        if path.exists():
            return path
    raise FileNotFoundError(
        f"Scaffold Map config not found for course '{course_id}' "
        f"(tried scaffold_map_, constitution_, lsm_ prefixes)"
    )


def load_scaffold_map(course_id: str | None = None, path: Path | None = None) -> ScaffoldMapConfig:
    if path is None:
        if course_id is None:
            course_id = "python_intro"
        path = _scaffold_map_path(course_id)
    if not path.exists():
        raise FileNotFoundError(f"Scaffold Map config not found: {path}")
    data = load_yaml(path)
    return ScaffoldMapConfig.model_validate(data)


def load_constitution(course_id: str | None = None, path: Path | None = None) -> ScaffoldMapConfig:
    """Backward-compatible alias."""
    return load_scaffold_map(course_id=course_id, path=path)


def load_lsm(course_id: str | None = None, path: Path | None = None) -> ScaffoldMapConfig:
    """Backward-compatible alias."""
    return load_scaffold_map(course_id=course_id, path=path)


def list_courses() -> list[dict[str, str]]:
    courses: list[dict[str, str]] = []
    seen: set[str] = set()
    for pattern in ("scaffold_map_*.yaml", "constitution_*.yaml", "lsm_*.yaml"):
        for path in sorted(CONFIGS_DIR.glob(pattern)):
            data = load_yaml(path)
            stem = path.stem
            for prefix in ("scaffold_map_", "constitution_", "lsm_"):
                if stem.startswith(prefix):
                    stem = stem[len(prefix) :]
                    break
            cid = data.get("course_id", stem)
            if cid in seen:
                continue
            seen.add(cid)
            courses.append(
                {
                    "course_id": cid,
                    "name": data.get("name", cid),
                    "path": str(path),
                }
            )
    return courses


def save_scaffold_map(config: ScaffoldMapConfig, path: Path | None = None) -> Path:
    """Persist Scaffold Map to disk (research/dev only — not exposed in product UI)."""
    if path is None:
        path = CONFIGS_DIR / f"scaffold_map_{config.course_id}.yaml"
    payload = config.model_dump(mode="json")
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(payload, f, sort_keys=False, allow_unicode=True)
    return path


def save_constitution(config: ScaffoldMapConfig, path: Path | None = None) -> Path:
    return save_scaffold_map(config, path=path)


def save_lsm(config: ScaffoldMapConfig, path: Path | None = None) -> Path:
    return save_scaffold_map(config, path=path)
