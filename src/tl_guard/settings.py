"""Runtime settings for TL-Guard LLM backends."""

from __future__ import annotations

import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    """
    LLM priority:
      1. TL_GUARD_LLM=openai + OPENAI_API_KEY → OpenAI
      2. Default → Ollama at TL_GUARD_OLLAMA_BASE_URL
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    tl_guard_llm: str = Field(default="ollama", alias="TL_GUARD_LLM")
    tl_guard_model: str = Field(default="llama3", alias="TL_GUARD_MODEL")
    tl_guard_ollama_base_url: str = Field(
        default="http://127.0.0.1:11434", alias="TL_GUARD_OLLAMA_BASE_URL"
    )
    tl_guard_ollama_timeout: float = Field(default=120.0, alias="TL_GUARD_OLLAMA_TIMEOUT")
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", alias="TL_GUARD_OPENAI_MODEL")

    @property
    def provider(self) -> str:
        raw = (self.tl_guard_llm or "ollama").strip().lower()
        if raw == "openai" and self.openai_api_key:
            return "openai"
        return "ollama"

    @property
    def model_name(self) -> str:
        if self.provider == "openai":
            return os.getenv("TL_GUARD_MODEL", self.openai_model)
        return self.tl_guard_model


@lru_cache
def get_settings() -> Settings:
    return Settings()
