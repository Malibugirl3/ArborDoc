"""
@file cli.py
@brief Command-line interface for ArborDoc.

@author Ma PingChuan, Shi Kaibo
@copyright Copyright (c) 2026 Ma PingChuan, Shi Kaibo. SPDX-License-Identifier: MIT
@date 2026
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import List, Optional

from arbordoc.assist.config import load_assist_config
from arbordoc.assist.pipeline import apply_merge_instructions, prepare_assist_workspace
from arbordoc.converters.latex import LatexExporter
from arbordoc.core.parser import parse_docx
from arbordoc.core.styler import transform_docx
from arbordoc.core.tree import write_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="arbordoc", description="Structured DOCX parsing toolkit.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    parse_parser = subparsers.add_parser("parse", help="Parse a DOCX file into JSON.")
    parse_parser.add_argument("-i", "--input", required=True, help="Input DOCX file path.")
    parse_parser.add_argument("-o", "--output", required=True, help="Output JSON file path.")

    transform_parser = subparsers.add_parser("transform", help="Rebuild a DOCX file into a template.")
    transform_parser.add_argument("-i", "--input", required=True, help="Source DOCX file path.")
    transform_parser.add_argument("-t", "--template", required=True, help="Template DOCX file path.")
    transform_parser.add_argument("-o", "--output", required=True, help="Output DOCX file path.")

    latex_parser = subparsers.add_parser("export-latex", help="Export a DOCX file to baseline LaTeX.")
    latex_parser.add_argument("-i", "--input", required=True, help="Input DOCX file path.")
    latex_parser.add_argument("-o", "--output", required=True, help="Output TEX file path.")
    latex_parser.add_argument(
        "--fragment",
        action="store_true",
        help="Write only body fragment (without documentclass/begin/end document).",
    )

    assist_parser = subparsers.add_parser(
        "assist",
        help="Human-readable review + merge gate (LLM optional, never silent).",
    )
    assist_sub = assist_parser.add_subparsers(dest="assist_command", required=True)

    prep = assist_sub.add_parser(
        "prepare",
        help="Snapshot DocTree, write assist_review.md and merge_instructions.json.",
    )
    prep.add_argument("-i", "--input", required=True, help="Source DOCX file path.")
    prep.add_argument("-w", "--workspace", required=True, help="Workspace directory path.")
    prep.add_argument(
        "--no-llm",
        action="store_true",
        help="Force-disable LLM for this workspace (overrides config).",
    )
    prep.add_argument(
        "--config",
        default=None,
        help="Path to arbordoc JSON config (or set ARBORDOC_CONFIG).",
    )

    apply_p = assist_sub.add_parser(
        "apply",
        help="Validate merge_instructions.json and write tree.merged.json.",
    )
    apply_p.add_argument("-w", "--workspace", required=True, help="Workspace directory path.")

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "parse":
        root = parse_docx(args.input)
        write_json(root, args.output)
        return 0

    if args.command == "transform":
        transform_docx(args.input, args.template, args.output)
        return 0

    if args.command == "export-latex":
        root = parse_docx(args.input)
        rendered = LatexExporter(standalone=not args.fragment).export(root)
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered, encoding="utf-8")
        return 0

    if args.command == "assist":
        if args.assist_command == "prepare":
            cfg = load_assist_config(Path(args.config) if args.config else None)
            llm_allowed = bool(cfg.llm_enabled_default) and not args.no_llm
            prepare_assist_workspace(
                Path(args.input),
                Path(args.workspace),
                llm_allowed=llm_allowed,
            )
            return 0
        if args.assist_command == "apply":
            path = apply_merge_instructions(Path(args.workspace))
            print(f"Wrote merged tree to {path}")
            return 0

    raise ValueError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
