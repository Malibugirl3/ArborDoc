"""Prepare assist workspace artifacts and apply validated merge instructions."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import TypeAdapter

from arbordoc.core.parser import parse_docx
from arbordoc.core.tree import write_json
from arbordoc.assist.review import build_assist_review_markdown
from arbordoc.assist.schema import MergeInstructions
from arbordoc.models.schema import DocNode


def prepare_assist_workspace(
    input_docx: Path,
    workspace_dir: Path,
    *,
    llm_allowed: bool = False,
) -> Path:
    """Write baseline tree JSON, human-readable review, default merge instructions."""
    workspace_dir.mkdir(parents=True, exist_ok=True)
    root = parse_docx(input_docx)

    base_path = workspace_dir / "tree.base.json"
    write_json(root, base_path)

    review_path = workspace_dir / "assist_review.md"
    review_path.write_text(build_assist_review_markdown(root), encoding="utf-8")

    instructions = MergeInstructions(tree_source="base")
    inst_path = workspace_dir / "merge_instructions.json"
    inst_path.write_text(
        instructions.model_dump_json(indent=2),
        encoding="utf-8",
    )

    marker = workspace_dir / ".arbordoc_workspace"
    marker.write_text(
        json.dumps({"input_docx": str(input_docx.resolve()), "llm_allowed": llm_allowed}, indent=2),
        encoding="utf-8",
    )

    return workspace_dir


def prepare_assist_with_llm(
    input_docx: Path,
    workspace_dir: Path,
    api_key: str,
    *,
    model: str = "deepseek-chat",
    base_url: str = "https://api.deepseek.com",
) -> Path:
    """Prepare workspace and generate an LLM structural analysis."""
    from arbordoc.assist.llm import analyse_with_llm
    from arbordoc.core.parser import parse_docx

    prepare_assist_workspace(input_docx, workspace_dir, llm_allowed=True)
    tree = parse_docx(input_docx)
    _, ai_analysis = analyse_with_llm(tree, api_key=api_key)
    (workspace_dir / "assist_ai_analysis.md").write_text(ai_analysis, encoding="utf-8")
    return workspace_dir


def apply_merge_instructions(workspace_dir: Path) -> Path:
    """Read merge_instructions.json and emit tree.merged.json (never touches DOCX)."""
    inst_path = workspace_dir / "merge_instructions.json"
    if not inst_path.is_file():
        raise FileNotFoundError(f"Missing {inst_path}")

    instructions = MergeInstructions.model_validate_json(inst_path.read_text(encoding="utf-8"))

    if instructions.tree_source == "base":
        base_path = workspace_dir / "tree.base.json"
        if not base_path.is_file():
            raise FileNotFoundError(f"Missing {base_path}")
        merged = TypeAdapter(DocNode).validate_json(base_path.read_text(encoding="utf-8"))
    else:
        prop_path = workspace_dir / instructions.proposed_filename()
        if not prop_path.is_file():
            raise FileNotFoundError(
                f"tree_source is proposed but {prop_path} does not exist.",
            )
        merged = TypeAdapter(DocNode).validate_json(prop_path.read_text(encoding="utf-8"))

    out = workspace_dir / "tree.merged.json"
    write_json(merged, out)
    return out


def export_json_root(root: DocNode, output_path: Path) -> Path:
    """Utility for tests / LLM adapters writing proposed trees."""
    write_json(root, output_path)
    return output_path
