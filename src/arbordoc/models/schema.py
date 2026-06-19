"""
@file schema.py
@brief Pydantic models for ArborDoc document structures.

@author Ma PingChuan, Shi Kaibo
@copyright Copyright (c) 2026 Ma PingChuan, Shi Kaibo. SPDX-License-Identifier: MIT
@date 2026

These models are independent from python-docx objects and describe
ArborDoc's semantic structure for extraction, parsing, and export.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional, Union
from uuid import uuid4

from pydantic import BaseModel, Field


class NodeType(str, Enum):
    """Node types for the document tree."""

    DOCUMENT = "document"
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    TABLE = "table"
    IMAGE = "image"
    HEADER = "header"
    FOOTER = "footer"


class BlockType(str, Enum):
    """Linear block types used between extraction and parsing."""

    HEADING = "heading"
    PARAGRAPH = "paragraph"
    TABLE = "table"
    IMAGE = "image"
    HEADER = "header"
    FOOTER = "footer"


class InlineElementType(str, Enum):
    """Types of inline content within a paragraph or heading."""

    TEXT_RUN = "text_run"
    HYPERLINK_RUN = "hyperlink_run"
    INLINE_IMAGE = "inline_image"


class RunFormat(BaseModel):
    """Formatting properties of a single text run."""

    bold: Optional[bool] = None
    italic: Optional[bool] = None
    underline: Optional[bool] = None
    strikethrough: Optional[bool] = None
    superscript: Optional[bool] = None
    subscript: Optional[bool] = None
    font_name: Optional[str] = None
    font_size_pt: Optional[float] = None
    font_color_rgb: Optional[str] = None
    highlight_color: Optional[str] = None
    style_name: Optional[str] = None


class TextRun(BaseModel):
    """A text run with formatting."""

    type: InlineElementType = Field(default=InlineElementType.TEXT_RUN)
    text: str = ""
    format: RunFormat = Field(default_factory=RunFormat)


class HyperlinkRun(BaseModel):
    """A hyperlink containing formatted text runs."""

    type: InlineElementType = Field(default=InlineElementType.HYPERLINK_RUN)
    url: str = ""
    children: list[TextRun] = Field(default_factory=list)


class InlineImageInline(BaseModel):
    """An image anchored inline within a paragraph."""

    type: InlineElementType = Field(default=InlineElementType.INLINE_IMAGE)
    relationship_id: str = ""


InlineElement = Union[TextRun, HyperlinkRun, InlineImageInline]


class ParagraphFormat(BaseModel):
    """Paragraph-level formatting."""

    alignment: Optional[str] = None
    line_spacing: Optional[float] = None
    line_spacing_rule: Optional[str] = None
    space_before: Optional[float] = None
    space_after: Optional[float] = None
    left_indent: Optional[float] = None
    right_indent: Optional[float] = None
    first_line_indent: Optional[float] = None
    page_break_before: Optional[bool] = None
    keep_lines_together: Optional[bool] = None
    keep_with_next: Optional[bool] = None
    style_name: Optional[str] = None


class ListInfo(BaseModel):
    """List numbering information for a paragraph."""

    num_id: int
    level: int = 0
    is_ordered: bool = False


class DocBlock(BaseModel):
    """A linear content block extracted from a DOCX document."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    type: BlockType
    text: Optional[str] = None
    level: int = 0
    meta: dict[str, Any] = Field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump(mode="json")


class DocNode(BaseModel):
    """A node in ArborDoc's logical document tree."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    type: NodeType
    level: int = 0
    text: Optional[str] = None
    meta: dict[str, Any] = Field(default_factory=dict)
    children: list["DocNode"] = Field(default_factory=list)
    inline_content: Optional[list[InlineElement]] = None
    list_info: Optional[ListInfo] = None
    paragraph_format: Optional[ParagraphFormat] = None

    def add_child(self, child: "DocNode") -> "DocNode":
        self.children.append(child)
        return child

    def iter_depth_first(self) -> list["DocNode"]:
        nodes = [self]
        for child in self.children:
            nodes.extend(child.iter_depth_first())
        return nodes

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump(mode="json")


DocBlock.model_rebuild()
DocNode.model_rebuild()
