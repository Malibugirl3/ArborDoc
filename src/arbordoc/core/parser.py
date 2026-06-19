"""
@file parser.py
@brief Build a logical document tree from extracted DOCX blocks.

@author Ma PingChuan, Shi Kaibo
@copyright Copyright (c) 2026 Ma PingChuan, Shi Kaibo. SPDX-License-Identifier: MIT
@date 2026

Consumes DocBlock linear blocks (not raw python-docx objects) and applies
ArborDoc structure-building rules to produce a DocTree.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Optional, Union

from docx import Document
from docx.document import Document as DocumentObject

from arbordoc.core.extractor import extract_all, resolve_list_is_ordered
from arbordoc.core.tree import append_child, create_root
from arbordoc.models.schema import (
    BlockType,
    DocBlock,
    DocNode,
    HyperlinkRun,
    InlineElement,
    InlineImageInline,
    ListInfo,
    NodeType,
    ParagraphFormat,
    RunFormat,
    TextRun,
)


def _build_inline_content(meta: dict) -> Optional[list[InlineElement]]:
    """Build inline_content from meta runs and hyperlinks extracted from a paragraph."""
    runs_raw = meta.get("runs", [])
    links_raw = meta.get("hyperlinks", [])
    image_rel_ids = meta.get("image_rel_ids", [])

    if not runs_raw and not links_raw and not image_rel_ids:
        return None

    inline: list[InlineElement] = []

    for img_rid in image_rel_ids:
        inline.append(InlineImageInline(relationship_id=str(img_rid)))

    for run_data in runs_raw:
        if not isinstance(run_data, dict):
            continue
        text = str(run_data.get("text", ""))
        if not text:
            continue
        fmt_raw = run_data.get("format", {}) or {}
        fmt = RunFormat(
            bold=fmt_raw.get("bold"),
            italic=fmt_raw.get("italic"),
            underline=fmt_raw.get("underline"),
            strikethrough=fmt_raw.get("strikethrough"),
            superscript=fmt_raw.get("superscript"),
            subscript=fmt_raw.get("subscript"),
            font_name=fmt_raw.get("font_name"),
            font_size_pt=fmt_raw.get("font_size_pt"),
            font_color_rgb=fmt_raw.get("font_color_rgb"),
            highlight_color=fmt_raw.get("highlight_color"),
            style_name=fmt_raw.get("style_name"),
        )
        inline.append(TextRun(text=text, format=fmt))

    for link_data in links_raw:
        if not isinstance(link_data, dict):
            continue
        url = str(link_data.get("url", ""))
        children: list[TextRun] = []
        for child_data in link_data.get("children", []) or []:
            if not isinstance(child_data, dict):
                continue
            child_fmt_raw = child_data.get("format", {}) or {}
            child_fmt = RunFormat(
                bold=child_fmt_raw.get("bold"),
                italic=child_fmt_raw.get("italic"),
                underline=child_fmt_raw.get("underline"),
                strikethrough=child_fmt_raw.get("strikethrough"),
                superscript=child_fmt_raw.get("superscript"),
                subscript=child_fmt_raw.get("subscript"),
                font_name=child_fmt_raw.get("font_name"),
                font_size_pt=child_fmt_raw.get("font_size_pt"),
                font_color_rgb=child_fmt_raw.get("font_color_rgb"),
                highlight_color=child_fmt_raw.get("highlight_color"),
                style_name=child_fmt_raw.get("style_name"),
            )
            children.append(TextRun(text=str(child_data.get("text", "")), format=child_fmt))
        inline.append(HyperlinkRun(url=url, children=children))

    return inline if inline else None


def _build_paragraph_format(block_meta: dict) -> Optional[ParagraphFormat]:
    """Build ParagraphFormat from block meta if present."""
    pf_raw = block_meta.get("paragraph_format")
    if not isinstance(pf_raw, dict) or not pf_raw:
        return None
    return ParagraphFormat(
        alignment=pf_raw.get("alignment"),
        line_spacing=pf_raw.get("line_spacing"),
        line_spacing_rule=pf_raw.get("line_spacing_rule"),
        space_before=pf_raw.get("space_before"),
        space_after=pf_raw.get("space_after"),
        left_indent=pf_raw.get("left_indent"),
        right_indent=pf_raw.get("right_indent"),
        first_line_indent=pf_raw.get("first_line_indent"),
        page_break_before=pf_raw.get("page_break_before"),
        keep_lines_together=pf_raw.get("keep_lines_together"),
        keep_with_next=pf_raw.get("keep_with_next"),
        style_name=pf_raw.get("style_name"),
    )


def _build_meta(base_meta: dict, block_meta: dict) -> dict:
    """Merge block meta into base meta, keeping only keys relevant for DocNode."""
    result = {k: v for k, v in base_meta.items()}
    style = block_meta.get("style")
    if style is not None:
        result["style"] = style
    para_format = block_meta.get("paragraph_format")
    if para_format:
        result["paragraph_format"] = para_format
    list_info = block_meta.get("list_info")
    if list_info:
        result["list_info"] = list_info
    image_rel_ids = block_meta.get("image_rel_ids", [])
    if image_rel_ids:
        result["image_rel_ids"] = image_rel_ids
    return result


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
        block_meta = block.meta

        if block.type in (BlockType.HEADER, BlockType.FOOTER):
            container_type = NodeType.HEADER if block.type == BlockType.HEADER else NodeType.FOOTER
            section_idx = block_meta.get("section_index", 0)
            hdr_type = block_meta.get("header_type", "default")

            # Find or create container node under root
            container = None
            for child in root.children:
                if (
                    child.type == container_type
                    and child.meta.get("section_index") == section_idx
                    and child.meta.get("header_type") == hdr_type
                ):
                    container = child
                    break
            if container is None:
                container = DocNode(
                    type=container_type,
                    level=0,
                    meta={"section_index": section_idx, "header_type": hdr_type},
                )
                root.children.insert(
                    sum(1 for c in root.children if c.type in (NodeType.HEADER, NodeType.FOOTER)),
                    container,
                )

            # Add content node (paragraph or table) as child of container
            content_node = DocNode(
                type=NodeType.PARAGRAPH if block.text is not None or block.meta.get("runs") else NodeType.TABLE,
                level=1,
                text=block.text,
                meta=_build_meta({"style": block_meta.get("style")}, block_meta),
                inline_content=_build_inline_content(block_meta),
                paragraph_format=_build_paragraph_format(block_meta),
            )
            container.children.append(content_node)
            continue

        if block.type == BlockType.HEADING:
            while len(stack) - 1 >= block.level:
                stack.pop()

            heading = DocNode(
                type=NodeType.HEADING,
                level=block.level,
                text=block.text,
                meta=_build_meta({"style": block_meta.get("style")}, block_meta),
                inline_content=_build_inline_content(block_meta),
                paragraph_format=_build_paragraph_format(block_meta),
            )
            append_child(stack[-1], heading)
            stack.append(heading)

            for relation_id in block_meta.get("image_rel_ids", []):
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
            list_info_raw = block_meta.get("list_info")
            list_info = None
            if isinstance(list_info_raw, dict):
                list_info = ListInfo(
                    num_id=int(list_info_raw.get("num_id", 0)),
                    level=int(list_info_raw.get("level", 0)),
                    is_ordered=bool(list_info_raw.get("is_ordered", False)),
                )

            paragraph = DocNode(
                type=NodeType.PARAGRAPH,
                level=max(len(stack) - 1, 0),
                text=block.text,
                meta=_build_meta(
                    {
                        "style": block_meta.get("style"),
                        "image_rel_ids": block_meta.get("image_rel_ids", []),
                    },
                    block_meta,
                ),
                inline_content=_build_inline_content(block_meta),
                list_info=list_info,
                paragraph_format=_build_paragraph_format(block_meta),
            )
            append_child(parent, paragraph)

            for relation_id in block_meta.get("image_rel_ids", []):
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
    blocks, extra = extract_all(document)
    for block in blocks:
        li = block.meta.get("list_info")
        if isinstance(li, dict) and not li.get("is_ordered"):
            li["is_ordered"] = resolve_list_is_ordered(document, int(li.get("num_id", 0)))
    root = build_tree_from_blocks(blocks, source_path=source_path)
    if extra.get("sections"):
        root.meta["sections"] = extra["sections"]
    return root


def parse_docx(path: Union[str, Path]) -> DocNode:
    """Load a DOCX file from disk and parse it into a tree."""
    source = Path(path)
    document = Document(source)
    return parse_document(document, source_path=str(source))
