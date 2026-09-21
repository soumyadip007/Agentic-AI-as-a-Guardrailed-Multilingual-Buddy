"""LLM backends: Ollama (default) or OpenAI. No mock tutor in production."""

from __future__ import annotations

import logging
from typing import Protocol

import httpx
from openai import OpenAI

from tl_guard.models import ScaffoldTier
from tl_guard.settings import Settings, get_settings

logger = logging.getLogger(__name__)


TIER_INSTRUCTIONS = {
    ScaffoldTier.T1: (
        "Give only a short nudge or hint. Do NOT provide worked steps, full code, or the final answer."
    ),
    ScaffoldTier.T2: (
        "Give a conceptual explanation in the student's terms. Do NOT provide a full worked solution or complete code."
    ),
    ScaffoldTier.T3: (
        "Give a worked example with key steps. Omit the final boxed answer or complete copy-paste solution if possible."
    ),
    ScaffoldTier.T4: (
        "You may provide a full solution. Still teach; do not just dump code without explanation."
    ),
}

STANCE_PREAMBLE = (
    "You are TL-Guard, a multilingual tutoring buddy. "
    "Translanguaging is welcome: students may mix languages. "
    "Never punish or shame language mixing. "
    "Stay within the authorized scaffold tier and response language."
)


class LLMClient(Protocol):
    def complete(self, system: str, user: str) -> str: ...


class LLMError(RuntimeError):
    """Raised when the configured LLM backend cannot complete a request."""


class OllamaLLM:
    """Local Ollama chat backend (OpenAI-compatible /api/chat)."""

    def __init__(
        self,
        model: str | None = None,
        base_url: str | None = None,
        timeout: float | None = None,
        settings: Settings | None = None,
    ) -> None:
        cfg = settings or get_settings()
        self.model = model or cfg.tl_guard_model
        self.base_url = (base_url or cfg.tl_guard_ollama_base_url).rstrip("/")
        self.timeout = timeout if timeout is not None else cfg.tl_guard_ollama_timeout

    def complete(self, system: str, user: str) -> str:
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "stream": False,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "options": {"temperature": 0.4},
        }
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()
        except httpx.ConnectError as e:
            raise LLMError(
                f"Cannot reach Ollama at {self.base_url}. "
                "Start it with `ollama serve` and pull a model "
                f"(e.g. `ollama pull {self.model}`)."
            ) from e
        except httpx.HTTPStatusError as e:
            detail = e.response.text[:300]
            raise LLMError(
                f"Ollama HTTP {e.response.status_code} for model '{self.model}': {detail}"
            ) from e
        except httpx.TimeoutException as e:
            raise LLMError(
                f"Ollama timed out after {self.timeout}s (model={self.model})."
            ) from e

        message = data.get("message") or {}
        content = (message.get("content") or "").strip()
        if not content:
            raise LLMError(f"Ollama returned an empty response for model '{self.model}'.")
        return content

    def ping(self) -> dict:
        """Return /api/tags payload to verify connectivity."""
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(f"{self.base_url}/api/tags")
            resp.raise_for_status()
            return resp.json()


class OpenAILLM:
    def __init__(
        self,
        model: str | None = None,
        api_key: str | None = None,
        settings: Settings | None = None,
    ) -> None:
        cfg = settings or get_settings()
        key = api_key or cfg.openai_api_key
        if not key:
            raise LLMError("OPENAI_API_KEY is required when TL_GUARD_LLM=openai.")
        self.client = OpenAI(api_key=key)
        self.model = model or cfg.model_name

    def complete(self, system: str, user: str) -> str:
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=0.4,
            )
        except Exception as e:
            raise LLMError(f"OpenAI request failed: {e}") from e
        return (resp.choices[0].message.content or "").strip()


def get_llm(settings: Settings | None = None) -> LLMClient:
    """
    Resolve the production LLM client.

    Default: Ollama (`llama3` unless TL_GUARD_MODEL is set).
    Optional: set TL_GUARD_LLM=openai and OPENAI_API_KEY.
    """
    cfg = settings or get_settings()
    if cfg.provider == "openai":
        logger.info("Using OpenAI model=%s", cfg.model_name)
        return OpenAILLM(settings=cfg)
    logger.info(
        "Using Ollama model=%s base_url=%s", cfg.tl_guard_model, cfg.tl_guard_ollama_base_url
    )
    return OllamaLLM(settings=cfg)


def build_system_prompt(*, tier: ScaffoldTier, language: str, course: str, concept: str) -> str:
    lang_line = {
        "en": "Respond in English.",
        "hi": "Respond in Hindi (Devanagari or clear Hinglish if needed).",
        "bn": "Respond in Bengali.",
        "es": "Respond in Spanish.",
        "mixed": "Respond in mixed student-friendly language (e.g. Hinglish).",
    }.get(language, "Respond in English.")
    return (
        f"{STANCE_PREAMBLE}\n"
        f"Course: {course}. Concept: {concept}.\n"
        f"Authorized scaffold tier: {tier.value}. {TIER_INSTRUCTIONS[tier]}\n"
        f"{lang_line}\n"
    )
