"""Classify language-switch intent: legitimate / adversarial / neutral."""

from __future__ import annotations

import re
from dataclasses import dataclass

from tl_guard.models import LanguageIntent


ANSWER_SEEKING = [
    r"\bfull (code|solution|answer)\b",
    r"\bjust (give|tell|write)\b",
    r"\bcomplete (code|solution)\b",
    r"\bgive me the answer\b",
    r"\bwrite (the )?entire\b",
    r"\bsolve (it|this) (for me|completely)\b",
    r"पूरा (कोड|उत्तर|जवाब)",
    r"सीधा जवाब",
    r"সম্পূর্ণ উত্তর",
    r"respuesta completa",
    r"dame la (respuesta|soluci[oó]n)",
]

CLARIFICATION = [
    r"\bwhat does .+ mean\b",
    r"\bexplain .+ in\b",
    r"\bin (simple|hindi|bengali|spanish)\b",
    r"\bmatlab\b",
    r"\bsamjhao\b",
    r"\bbujhate\b",
    r"समझाओ",
    r"मतलब",
    r"বোঝাও",
    r"expl[ií]came",
]


@dataclass
class IntentResult:
    intent: LanguageIntent
    confidence: float
    reasons: list[str]


def classify_intent(
    message: str,
    *,
    previous_language: str | None,
    current_language: str,
    mastery: float,
    asked_same_before: bool = False,
    last_authorized_tier: str | None = None,
) -> IntentResult:
    """Rule-based intent classifier using mastery + switch + answer-seeking cues."""
    if previous_language is None or previous_language == current_language:
        # No switch — still check adversarial answer-seeking in same language
        if _matches(message, ANSWER_SEEKING) and mastery < 0.6:
            return IntentResult(
                LanguageIntent.ADVERSARIAL,
                0.7,
                ["answer-seeking phrasing without language switch"],
            )
        return IntentResult(LanguageIntent.NONE, 0.9, ["no language switch"])

    reasons: list[str] = [f"switch {previous_language} → {current_language}"]
    score_adv = 0.0
    score_leg = 0.0

    if _matches(message, ANSWER_SEEKING):
        score_adv += 0.45
        reasons.append("answer-seeking phrasing")
    if asked_same_before:
        score_adv += 0.35
        reasons.append("re-ask after language switch")
    if last_authorized_tier in {"T1", "T2"} and _matches(message, ANSWER_SEEKING):
        score_adv += 0.2
        reasons.append("seeking higher disclosure after restricted tier")
    if mastery < 0.35 and _matches(message, CLARIFICATION):
        score_leg += 0.5
        reasons.append("low mastery + clarification request")
    if _matches(message, CLARIFICATION):
        score_leg += 0.35
        reasons.append("clarification / vocabulary request")
    if current_language in {"hi", "bn", "es", "mixed"} and not _matches(message, ANSWER_SEEKING):
        score_leg += 0.2
        reasons.append("L2 use without extraction cues")

    if score_adv >= 0.55 and score_adv > score_leg:
        return IntentResult(LanguageIntent.ADVERSARIAL, min(0.95, score_adv), reasons)
    if score_leg >= 0.4:
        return IntentResult(LanguageIntent.LEGITIMATE, min(0.95, score_leg), reasons)
    return IntentResult(LanguageIntent.NEUTRAL, 0.6, reasons + ["preference switch"])


def _matches(text: str, patterns: list[str]) -> bool:
    return any(re.search(p, text, flags=re.IGNORECASE) for p in patterns)


def similar_question(a: str, b: str) -> bool:
    """Crude re-ask detector via token Jaccard overlap."""
    ta = {t.lower() for t in re.findall(r"[A-Za-z\u0900-\u09FF]+", a)}
    tb = {t.lower() for t in re.findall(r"[A-Za-z\u0900-\u09FF]+", b)}
    if not ta or not tb:
        return False
    return len(ta & tb) / len(ta | tb) >= 0.55
