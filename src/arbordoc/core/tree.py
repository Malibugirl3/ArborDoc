"""Helpers for building and exporting document trees.

The tree layer is ArborDoc's format-neutral middle representation.
Parser modules build this structure from DOCX, and later styler/exporter
modules consume the same structure for reconstruction or conversion.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterator, Optional, Union

from arbordoc.models.schema import DocNode, NodeType


def create_root(meta: Optional[dict] = None) -> DocNode:
    """Create the root document node."""
    return DocNode(type=NodeType.DOCUMENT, level=0, text=None, meta=meta or {})


def append_child(parent: DocNode, child: DocNode) -> DocNode:
    """Attach a child node to a parent."""
    return parent.add_child(child)


def walk_depth_first(node: DocNode, *, skip_root: bool = False) -> Iterator[DocNode]:
    """Yield nodes in depth-first order."""
    # Keeping traversal separate from parsing makes the tree reusable:
    # the same DocTree can later drive JSON export, template rebuild,
    # or other exporters without depending on `python-docx` internals.
    if not skip_root:
        yield node
    for child in node.children:
        yield child
        yield from walk_depth_first(child, skip_root=True)


def to_dict(node: DocNode) -> dict:
    """Convert a tree to a plain dictionary."""
    return node.to_dict()


def to_json(node: DocNode, *, indent: int = 2) -> str:
    """Serialize a tree to a JSON string."""
    return json.dumps(to_dict(node), ensure_ascii=False, indent=indent)


def write_json(node: DocNode, output_path: Union[str, Path], *, indent: int = 2) -> Path:
    """Write a JSON snapshot of the tree to disk."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(to_json(node, indent=indent), encoding="utf-8")
    return path
