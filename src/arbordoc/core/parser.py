"""Parsing utilities that turn extracted blocks into a logical document tree.

This module consumes ArborDoc `DocBlock`s instead of raw `python-docx`
objects. That keeps extraction concerns separate from ArborDoc's own
structure-building rules.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Optional, Union

from docx import Document
from docx.document import Document as DocumentObject

from arbordoc.core.extractor import extract_blocks
from arbordoc.core.tree import append_child, create_root
from arbordoc.models.schema import BlockType, DocBlock, DocNode, NodeType


def build_tree_from_blocks(
    blocks: Iterable[DocBlock],
    *,
    source_path: Optional[str] = None,
) -> DocNode:
    """Build a logical document tree from ArborDoc's linear block list."""
    root = create_root(meta={"source_path": source_path} if source_path else {})
    stack: List[DocNode] = [root]

    for block in blocks:
        parent = stack[-1]

        if block.type == BlockType.HEADING:
            # Heading blocks are the only ones that change tree depth.
            while len(stack) - 1 >= block.level:
                stack.pop()

            heading = DocNode(
                type=NodeType.HEADING,
                level=block.level,
                text=block.text,
                meta={"style": block.meta.get("style")},
            )
            append_child(stack[-1], heading)
            stack.append(heading)

            for relation_id in block.meta.get("image_rel_ids", []):
                append_child(
                    heading,
                    DocNode(
                        type=NodeType.IMAGE,
                        level=block.level,
                        text=None,
                        meta={"relationship_id": relation_id},
                    ),
                )
            continue

        if block.type == BlockType.PARAGRAPH:
            paragraph = DocNode(
                type=NodeType.PARAGRAPH,
                level=max(len(stack) - 1, 0),
                text=block.text,
                meta={
                    "style": block.meta.get("style"),
                    "image_rel_ids": block.meta.get("image_rel_ids", []),
                },
            )
            append_child(parent, paragraph)

            for relation_id in block.meta.get("image_rel_ids", []):
                append_child(
                    paragraph,
                    DocNode(
                        type=NodeType.IMAGE,
                        level=paragraph.level,
                        text=None,
                        meta={"relationship_id": relation_id},
                    ),
                )
            continue

        if block.type == BlockType.IMAGE:
            append_child(
                parent,
                DocNode(
                    type=NodeType.IMAGE,
                    level=max(len(stack) - 1, 0),
                    text=block.text,
                    meta=block.meta,
                ),
            )
            continue

        table_node = DocNode(
            type=NodeType.TABLE,
            level=max(len(stack) - 1, 0),
            text=None,
            meta=block.meta,
        )
        append_child(parent, table_node)

    return root


def parse_document(document: DocumentObject, *, source_path: Optional[str] = None) -> DocNode:
    """Extract a loaded Word document and parse it into an ArborDoc tree."""
    blocks = extract_blocks(document)
    return build_tree_from_blocks(blocks, source_path=source_path)


def parse_docx(path: Union[str, Path]) -> DocNode:
    """Load a DOCX file from disk and parse it into a tree."""
    source = Path(path)
    document = Document(source)
    return parse_document(document, source_path=str(source))
