"""Language detection for English, Hindi, Bengali, Spanish, and code-mixed text."""

from __future__ import annotations

import re
from dataclasses import dataclass


DEVANAGARI = re.compile(r"[\u0900-\u097F]")
BENGALI = re.compile(r"[\u0980-\u09FF]")
LATIN = re.compile(r"[A-Za-z]")

# Common Hinglish / Indian English switch cues
HINGLISH_CUES = {
    "kya", "hai", "nahi", "matlab", "samjhao", "batao", "please", "kaise",
    "kyun", "kyu", "acha", "theek", "karo", "mujhe", "tum", "aap",
}
BANGLISH_CUES = {
    "ki", "kore", "bolo", "bujhte", "pari", "na", "ki", "amake", "tumi",
}
SPANISH_CUES = {
    "que", "qué", "como", "cómo", "por", "favor", "explicame", "explícame",
    "no", "entiendo", "ayuda", "porque", "porque", "esta", "está",
}
ENGLISH_CUES = {
    "what", "how", "why", "explain", "please", "help", "answer", "hint",
    "solution", "code", "function", "loop", "list", "vector", "matrix",
}


@dataclass
class LanguageDetection:
    language: str
    confidence: float
    is_code_mixed: bool
    script_hints: list[str]


def _token_set(text: str) -> set[str]:
    return {t.lower() for t in re.findall(r"[A-Za-zÀ-ÿ\u0900-\u09FF]+", text)}


def detect_language(text: str) -> LanguageDetection:
    """Heuristic multilingual + code-mix detector (no external model required)."""
    text = (text or "").strip()
    if not text:
        return LanguageDetection("en", 0.0, False, [])

    scripts: list[str] = []
    has_dev = bool(DEVANAGARI.search(text))
    has_bn = bool(BENGALI.search(text))
    has_latin = bool(LATIN.search(text))
    if has_dev:
        scripts.append("devanagari")
    if has_bn:
        scripts.append("bengali")
    if has_latin:
        scripts.append("latin")

    tokens = _token_set(text)
    scores = {
        "hi": len(tokens & HINGLISH_CUES) + (3.0 if has_dev else 0.0),
        "bn": len(tokens & BANGLISH_CUES) + (3.0 if has_bn else 0.0),
        "es": len(tokens & SPANISH_CUES) + (
            1.5 if any(c in text.lower() for c in ("á", "é", "í", "ó", "ú", "ñ", "¿", "¡")) else 0.0
        ),
        "en": len(tokens & ENGLISH_CUES) + (1.0 if has_latin and not has_dev and not has_bn else 0.0),
    }

    # Pure script dominance
    if has_dev and not has_latin and not has_bn:
        return LanguageDetection("hi", 0.95, False, scripts)
    if has_bn and not has_latin and not has_dev:
        return LanguageDetection("bn", 0.95, False, scripts)

    # Code-mixed: native script + Latin, or cue overlap across languages
    mixed = (has_dev and has_latin) or (has_bn and has_latin)
    cue_langs = [lang for lang, s in scores.items() if s >= 1.0]
    if mixed or len(cue_langs) >= 2:
        # Prefer the non-English cue language if present
        primary = max(("hi", "bn", "es"), key=lambda x: scores[x])
        if scores[primary] >= scores["en"]:
            return LanguageDetection(
                "mixed" if mixed else primary,
                0.7,
                True,
                scripts,
            )
        return LanguageDetection("mixed", 0.65, True, scripts)

    best = max(scores, key=scores.get)
    total = sum(scores.values()) or 1.0
    conf = min(0.99, 0.4 + scores[best] / total)
    if scores[best] == 0:
        return LanguageDetection("en", 0.5, False, scripts)
    return LanguageDetection(best, conf, False, scripts)
