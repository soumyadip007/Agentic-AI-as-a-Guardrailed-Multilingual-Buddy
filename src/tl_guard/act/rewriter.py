"""Rewrite over-disclosing responses down to the authorized tier."""

from __future__ import annotations

import re

from tl_guard.models import ScaffoldTier


SOLUTION_MARKERS = [
    r"```",
    r"\bdef\s+\w+\s*\(",
    r"\breturn\s+",
    r"\bfinal answer\b",
    r"\bcomplete (code|solution)\b",
    r"पूरा (हल|कोड)",
]


def looks_like_full_solution(text: str) -> bool:
    hits = sum(1 for p in SOLUTION_MARKERS if re.search(p, text, flags=re.IGNORECASE))
    return hits >= 2


def rewrite_to_tier(text: str, tier: ScaffoldTier, language: str = "en") -> str:
    """Deterministic rewrite that strips heavy disclosure."""
    if tier in {ScaffoldTier.T3, ScaffoldTier.T4} and not looks_like_full_solution(text):
        return text

    # Strip fenced code and dense solution lines
    stripped = re.sub(r"```[\s\S]*?```", "[code omitted by policy]", text)
    lines = []
    for line in stripped.splitlines():
        if re.search(r"^\s*def\s+|^\s*return\s+|^\s*class\s+", line):
            continue
        lines.append(line)
    body = "\n".join(lines).strip()
    if tier == ScaffoldTier.T1:
        prefix = {
            "hi": "संकेत (पुनर्लेखित नीति के अनुसार): ",
            "bn": "ইঙ্গিত (নীতি অনুসারে পুনর্লিখন): ",
            "es": "Pista (reescrita por política): ",
            "mixed": "Hint (policy rewrite): ",
        }.get(language, "Hint (rewritten to authorized tier): ")
        snippet = body.split(".")[0][:180]
        return f"{prefix}{snippet}. Try one small step yourself."
    if tier == ScaffoldTier.T2:
        prefix = {
            "hi": "अवधारणा (पुनर्लेखित): ",
            "bn": "ধারণা (পুনর্লিখন): ",
            "es": "Concepto (reescrito): ",
        }.get(language, "Concept (rewritten): ")
        return f"{prefix}{body[:400]}"
    return body[:600] or "Let's revisit the key idea without giving away the full solution."
