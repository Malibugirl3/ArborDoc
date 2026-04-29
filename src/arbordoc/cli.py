"""Command line interface for ArborDoc."""

from __future__ import annotations

import argparse
from typing import List, Optional

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

    raise ValueError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
