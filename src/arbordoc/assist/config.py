"""Local configuration for optional LLM profiles (default off)."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class LLMProfile(BaseModel):
    """Named endpoint profile (Phase 1 scaffold — callers validate keys via env)."""

    provider: str = Field(default="generic", description="Logical provider label.")
    api_base: Optional[str] = None
    model: Optional[str] = None
    api_key_env: Optional[str] = Field(
        default=None,
        description="Environment variable name that holds the secret.",
    )


class ArbordocAssistConfig(BaseModel):
    """User-level assist settings."""

    llm_enabled_default: bool = False
    profiles: Dict[str, LLMProfile] = Field(default_factory=dict)


DEFAULT_CONFIG_PATHS = (
    Path.cwd() / ".arbordoc" / "config.json",
    Path.home() / ".arbordoc" / "config.json",
)


def load_assist_config(path: Optional[Path] = None) -> ArbordocAssistConfig:
    """Load JSON config from explicit path, ``ARBORDOC_CONFIG``, or default search paths."""
    env_path = os.environ.get("ARBORDOC_CONFIG")
    candidates: list[Path] = []
    if path is not None:
        candidates.append(path)
    elif env_path:
        candidates.append(Path(env_path))
    else:
        candidates.extend(DEFAULT_CONFIG_PATHS)

    for candidate in candidates:
        if candidate.is_file():
            payload: Dict[str, Any] = json.loads(candidate.read_text(encoding="utf-8"))
            return ArbordocAssistConfig.model_validate(payload)

    return ArbordocAssistConfig()
