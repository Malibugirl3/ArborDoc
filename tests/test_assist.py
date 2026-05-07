"""Tests for assist workspace (local review + merge gate)."""

from __future__ import annotations

import json
from pathlib import Path

from arbordoc.assist.pipeline import apply_merge_instructions, prepare_assist_workspace
from arbordoc.assist.schema import MergeInstructions
from arbordoc.cli import main


def test_prepare_writes_review_and_base(sample_source_docx, tmp_path: Path) -> None:
    ws = tmp_path / "ws"
    prepare_assist_workspace(sample_source_docx, ws, llm_allowed=False)

    assert (ws / "tree.base.json").is_file()
    assert (ws / "assist_review.md").is_file()
    assert "Main Title" in (ws / "assist_review.md").read_text(encoding="utf-8")
    inst = MergeInstructions.model_validate_json((ws / "merge_instructions.json").read_text(encoding="utf-8"))
    assert inst.tree_source == "base"


def test_apply_roundtrip_base(sample_source_docx, tmp_path: Path) -> None:
    ws = tmp_path / "ws"
    prepare_assist_workspace(sample_source_docx, ws)
    merged_path = apply_merge_instructions(ws)

    assert merged_path.name == "tree.merged.json"
    payload = json.loads(merged_path.read_text(encoding="utf-8"))
    assert payload["type"] == "document"


def test_apply_with_proposed(sample_source_docx, tmp_path: Path) -> None:
    ws = tmp_path / "ws"
    prepare_assist_workspace(sample_source_docx, ws)

    proposed = ws / "tree.proposed.json"
    proposed.write_text((ws / "tree.base.json").read_text(encoding="utf-8"), encoding="utf-8")

    instructions = MergeInstructions(tree_source="proposed")
    (ws / "merge_instructions.json").write_text(instructions.model_dump_json(indent=2), encoding="utf-8")

    merged_path = apply_merge_instructions(ws)
    assert merged_path.is_file()


def test_cli_assist_prepare_apply(sample_source_docx, tmp_path: Path) -> None:
    ws = tmp_path / "ws_cli"
    assert main(["assist", "prepare", "-i", str(sample_source_docx), "-w", str(ws), "--no-llm"]) == 0
    assert main(["assist", "apply", "-w", str(ws)]) == 0
    assert (ws / "tree.merged.json").is_file()
