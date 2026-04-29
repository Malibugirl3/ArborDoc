"""Public package exports for ArborDoc.

The package surface exposes ArborDoc's own stable concepts:
- DocTree models
- parsing entry points
- reconstruction entry points

Callers should rely on these APIs instead of reaching directly into
`python-docx`, which stays as the low-level dependency layer.
"""

from arbordoc.core.extractor import extract_blocks
from arbordoc.core.parser import build_tree_from_blocks, parse_docx, parse_document
from arbordoc.core.styler import render_tree_to_template, transform_docx
from arbordoc.models.schema import BlockType, DocBlock, DocNode, NodeType

__all__ = [
    "BlockType",
    "DocBlock",
    "DocNode",
    "NodeType",
    "build_tree_from_blocks",
    "extract_blocks",
    "parse_docx",
    "parse_document",
    "render_tree_to_template",
    "transform_docx",
]
