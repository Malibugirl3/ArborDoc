"""Pydantic models representing ArborDoc's intermediate and tree structures.

These models are intentionally independent from `python-docx` objects.
They describe ArborDoc's own semantic structure so extracted blocks and
parsed trees can be reused by the CLI, styler, and future exporters.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class NodeType(str, Enum):
    """Minimal node types needed for Phase 1."""

    DOCUMENT = "document"
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    TABLE = "table"
    IMAGE = "image"


class BlockType(str, Enum):
    """Linear block types used between extraction and parsing."""

    HEADING = "heading"
    PARAGRAPH = "paragraph"
    TABLE = "table"
    IMAGE = "image"


class DocBlock(BaseModel):
    """A linear content block extracted from a DOCX document."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    type: BlockType
    text: Optional[str] = None
    level: int = 0
    meta: dict[str, Any] = Field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the block into plain JSON-compatible objects."""
        return self.model_dump(mode="json")


class DocNode(BaseModel):
    """A node in ArborDoc's logical document tree."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    type: NodeType
    level: int = 0
    text: Optional[str] = None
    meta: dict[str, Any] = Field(default_factory=dict)
    children: list["DocNode"] = Field(default_factory=list)

    def add_child(self, child: "DocNode") -> "DocNode":
        """Append a child node and return it for fluent tree building."""
        self.children.append(child)
        return child

    def iter_depth_first(self) -> list["DocNode"]:
        """Return a depth-first snapshot including the current node."""
        nodes = [self]
        for child in self.children:
            nodes.extend(child.iter_depth_first())
        return nodes

    def to_dict(self) -> dict[str, Any]:
        """Serialize the node tree into plain JSON-compatible objects."""
        return self.model_dump(mode="json")


DocBlock.model_rebuild()
DocNode.model_rebuild()
