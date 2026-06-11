"""Optional assist pipeline: human-readable review, merge discipline, LLM hooks."""

from arbordoc.assist.llm import analyse_with_llm
from arbordoc.assist.pipeline import (
    apply_merge_instructions,
    prepare_assist_with_llm,
    prepare_assist_workspace,
)

__all__ = [
    "analyse_with_llm",
    "apply_merge_instructions",
    "prepare_assist_with_llm",
    "prepare_assist_workspace",
]
