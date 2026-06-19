"""
@file __init__.py
@brief ArborDoc public package API.

@author Ma PingChuan, Shi Kaibo
@copyright Copyright (c) 2026 Ma PingChuan, Shi Kaibo. SPDX-License-Identifier: MIT
@date 2026

The package surface exposes ArborDoc's stable concepts: DocTree models,
parsing entry points, and reconstruction entry points.
"""

from arbordoc.assist.pipeline import apply_merge_instructions, prepare_assist_workspace
from arbordoc.converters.latex import LatexExporter
from arbordoc.core.extractor import extract_blocks
from arbordoc.core.parser import build_tree_from_blocks, parse_docx, parse_document
from arbordoc.core.styler import render_tree_to_template, transform_docx
from arbordoc.models.schema import (
    BlockType,
    DocBlock,
    DocNode,
    HyperlinkRun,
    InlineElementType,
    InlineImageInline,
    ListInfo,
    NodeType,
    ParagraphFormat,
    RunFormat,
    TextRun,
)

__all__ = [
    "BlockType",
    "DocBlock",
    "DocNode",
    "HyperlinkRun",
    "InlineElementType",
    "InlineImageInline",
    "LatexExporter",
    "ListInfo",
    "NodeType",
    "ParagraphFormat",
    "RunFormat",
    "TextRun",
    "apply_merge_instructions",
    "build_tree_from_blocks",
    "extract_blocks",
    "parse_docx",
    "parse_document",
    "prepare_assist_workspace",
    "render_tree_to_template",
    "transform_docx",
]
