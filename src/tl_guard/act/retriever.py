"""Local curriculum knowledge retriever for context-grounded Act.

Lexical (token-overlap) retrieval over markdown files under data/kb/{course_id}/.
No vector DB dependency — offline, reproducible, suitable for research demos.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_KB_ROOT = ROOT / "data" / "kb"

_TOKEN_RE = re.compile(r"[a-zA-Z0-9_\u0900-\u097F\u0980-\u09FF]+")


@dataclass(frozen=True)
class ContextChunk:
    source_id: str
    title: str
    text: str
    score: float


def _tokenize(text: str) -> set[str]:
    return {t.lower() for t in _TOKEN_RE.findall(text) if len(t) > 1}


def _chunk_markdown(text: str, source_id: str, max_chars: int = 600) -> list[tuple[str, str]]:
    """Split markdown into (title, body) chunks by headings or size."""
    parts: list[tuple[str, str]] = []
    sections = re.split(r"(?m)^(#{1,3}\s+.+)$", text)
    if len(sections) == 1:
        body = text.strip()
        if not body:
            return []
        title = source_id
        for i in range(0, len(body), max_chars):
            parts.append((title, body[i : i + max_chars].strip()))
        return parts

    # sections[0] may be preamble; then heading, body, heading, body, ...
    preamble = sections[0].strip()
    if preamble:
        parts.append((source_id, preamble[:max_chars]))
    i = 1
    while i + 1 < len(sections):
        heading = sections[i].lstrip("#").strip()
        body = sections[i + 1].strip()
        if body:
            for j in range(0, len(body), max_chars):
                parts.append((heading, body[j : j + max_chars].strip()))
        i += 2
    return parts


class KnowledgeRetriever:
    """Retrieve top-k curriculum snippets for a course/concept query."""

    def __init__(self, kb_root: Path | None = None) -> None:
        self.kb_root = kb_root or DEFAULT_KB_ROOT

    def retrieve(
        self,
        *,
        course_id: str,
        concept: str,
        query: str,
        top_k: int = 3,
    ) -> list[ContextChunk]:
        course_dir = self.kb_root / course_id
        if not course_dir.is_dir():
            return []

        candidates: list[ContextChunk] = []
        query_tokens = _tokenize(f"{concept} {query}")
        concept_stem = concept.strip().lower().replace(" ", "_")

        for path in sorted(course_dir.glob("*.md")):
            raw = path.read_text(encoding="utf-8")
            source_id = f"{course_id}/{path.stem}"
            boost = 1.5 if path.stem.lower() == concept_stem else 1.0
            for title, body in _chunk_markdown(raw, source_id=path.stem):
                doc_tokens = _tokenize(f"{title} {body}")
                if not doc_tokens or not query_tokens:
                    score = 0.1 * boost if path.stem.lower() == concept_stem else 0.0
                else:
                    overlap = len(query_tokens & doc_tokens)
                    score = (overlap / len(query_tokens)) * boost
                if score > 0:
                    candidates.append(
                        ContextChunk(
                            source_id=source_id,
                            title=title,
                            text=body,
                            score=round(score, 4),
                        )
                    )

        candidates.sort(key=lambda c: c.score, reverse=True)
        # Prefer concept file even if overlap is low
        if not candidates:
            concept_path = course_dir / f"{concept_stem}.md"
            if concept_path.exists():
                raw = concept_path.read_text(encoding="utf-8")
                chunks = _chunk_markdown(raw, source_id=concept_stem)
                if chunks:
                    title, body = chunks[0]
                    return [
                        ContextChunk(
                            source_id=f"{course_id}/{concept_stem}",
                            title=title,
                            text=body,
                            score=0.05,
                        )
                    ]
        return candidates[:top_k]
