"""Public package exports for ArborDoc.

The package surface exposes ArborDoc's own stable concepts:
- DocTree models
- parsing entry points
- reconstruction entry points

Callers should rely on these APIs instead of reaching directly into
`python-docx`, which stays as the low-level dependency layer.
"""

from arbordoc.assist.llm import analyse_with_llm
from arbordoc.assist.pipeline import apply_merge_instructions, prepare_assist_with_llm, prepare_assist_workspace
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
    "analyse_with_llm",
    "apply_merge_instructions",
    "build_tree_from_blocks",
    "extract_blocks",
    "parse_docx",
    "parse_document",
    "prepare_assist_with_llm",
    "prepare_assist_workspace",
    "render_tree_to_template",
    "transform_docx",
]
