"""Schemas for assist artifacts (review text vs machine instructions)."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class MergeInstructions(BaseModel):
    """Machine-readable apply gate. Human approval is implied by running ``apply``."""

    version: int = Field(default=1, ge=1, le=1)
    tree_source: Literal["base", "proposed"] = "base"
    proposed_relative: Optional[str] = Field(
        default=None,
        description="When tree_source is proposed, path relative to workspace dir.",
    )

    def proposed_filename(self) -> str:
        return self.proposed_relative or "tree.proposed.json"
