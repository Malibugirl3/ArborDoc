"""DOCX extraction helpers that normalize `python-docx` objects into blocks.

This module is ArborDoc's boundary with the low-level dependency layer:
- `python-docx` reads OOXML-backed document objects
- extractor functions translate those objects into ArborDoc `DocBlock`s
- higher layers can then parse blocks without depending on raw DOCX objects
"""

from __future__ import annotations

import re
import tempfile
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Union

from docx.document import Document as DocumentObject
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.oxml.ns import qn
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import Table
from docx.text.paragraph import Paragraph

from arbordoc.models.schema import BlockType, DocBlock

HEADING_STYLE_RE = re.compile(r"^(heading|标题)\s*(\d+)$", re.IGNORECASE)


def iter_block_items(document: DocumentObject) -> Iterator[Union[Paragraph, Table]]:
    """Yield paragraphs and tables in their original body order."""
    for child in document.element.body.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, document)
        elif isinstance(child, CT_Tbl):
            yield Table(child, document)


def extract_heading_level(paragraph: Paragraph) -> Optional[int]:
    """Infer heading depth from style name or outline level."""
    style_name = paragraph.style.name if paragraph.style is not None else ""
    match = HEADING_STYLE_RE.match(style_name.strip())
    if match:
        return int(match.group(2))

    p_pr = paragraph._element.pPr
    if p_pr is None:
        return None

    outline = p_pr.find(qn("w:outlineLvl"))
    if outline is None:
        return None

    value = outline.get(qn("w:val"))
    if value is None:
        return None

    return int(value) + 1


def extract_image_relation_ids(paragraph: Paragraph) -> List[str]:
    """Collect relationship ids for inline images inside a paragraph."""
    relation_ids: List[str] = []
    for blip in paragraph._element.xpath(".//*[local-name()='blip']"):
        relation_id = blip.get(qn("r:embed"))
        if relation_id:
            relation_ids.append(relation_id)
    return relation_ids


def get_image_blob(document: DocumentObject, relationship_id: str) -> Optional[bytes]:
    """Return PNG/JPEG/other image bytes for an ``r:id`` referencing an image part."""
    try:
        rel = document.part.rels[relationship_id]
    except KeyError:
        return None
    if rel.reltype != RT.IMAGE:
        return None
    part = rel.target_part
    blob = getattr(part, "blob", None)
    if blob is None:
        return None
    return bytes(blob)


def extract_image_blob_cache(document: DocumentObject) -> Dict[str, bytes]:
    """Map every embedded image ``r:id`` in the package to raw bytes (deduplicated)."""
    cache: Dict[str, bytes] = {}
    for rel_id, rel in document.part.rels.items():
        if rel.reltype != RT.IMAGE:
            continue
        blob = get_image_blob(document, rel_id)
        if blob is not None:
            cache[rel_id] = blob
    return cache


def extract_image_blob_cache_to_directory(
    document: DocumentObject,
    directory: Optional[Union[str, Path]] = None,
) -> tuple[Path, Dict[str, Path]]:
    """Write image blobs next to ``directory`` keyed by sanitized ``r:id`` filenames.

    If ``directory`` is omitted a temporary folder is created. Returns the directory path
    and a map from ``r:id`` → written file paths for reuse by styler or exporters.
    """
    base = Path(directory) if directory else Path(tempfile.mkdtemp(prefix="arbordoc_img_"))
    base.mkdir(parents=True, exist_ok=True)
    mem = extract_image_blob_cache(document)
    path_map: Dict[str, Path] = {}
    safe = re.compile(r"[^a-zA-Z0-9._-]")
    for rel_id, blob in mem.items():
        name = safe.sub("_", rel_id) + ".dat"
        out = base / name
        out.write_bytes(blob)
        path_map[rel_id] = out
    return base, path_map


def extract_run_format(run) -> dict[str, object]:
    """Read formatting properties from a python-docx Run."""
    font = run.font
    fmt: dict[str, object] = {}
    if font.bold is not None:
        fmt["bold"] = font.bold
    if font.italic is not None:
        fmt["italic"] = font.italic
    if font.underline is not None:
        fmt["underline"] = font.underline
    if font.strike is not None:
        fmt["strikethrough"] = font.strike
    if font.superscript is not None:
        fmt["superscript"] = font.superscript
    if font.subscript is not None:
        fmt["subscript"] = font.subscript
    if font.name is not None:
        fmt["font_name"] = font.name
    if font.size is not None:
        fmt["font_size_pt"] = font.size.pt
    if font.color and font.color.rgb is not None:
        fmt["font_color_rgb"] = str(font.color.rgb)
    if font.highlight_color is not None:
        fmt["highlight_color"] = str(font.highlight_color)
    if run.style is not None and run.style.name:
        fmt["style_name"] = run.style.name
    return fmt


def extract_runs_from_paragraph(paragraph: Paragraph) -> list[dict[str, object]]:
    """Extract text runs with formatting from a paragraph."""
    runs: list[dict[str, object]] = []
    for run in paragraph.runs:
        run_data: dict[str, object] = {
            "text": run.text,
            "format": extract_run_format(run),
        }
        runs.append(run_data)
    return runs


def extract_hyperlinks_from_paragraph(paragraph: Paragraph) -> list[dict[str, object]]:
    """Extract hyperlinks with their inner formatted runs."""
    links: list[dict[str, object]] = []
    for hyperlink in paragraph.hyperlinks:
        link_data: dict[str, object] = {
            "url": getattr(hyperlink, "url", "") or hyperlink.address or "",
            "children": [],
        }
        if hyperlink.runs:
            link_data["children"] = [
                {"text": r.text, "format": extract_run_format(r)}
                for r in hyperlink.runs
            ]
        else:
            link_data["children"] = [
                {"text": hyperlink.text or "", "format": {}}
            ]
        links.append(link_data)
    return links


def extract_paragraph_format(paragraph: Paragraph) -> dict[str, object]:
    """Read paragraph-level formatting properties."""
    pf = paragraph.paragraph_format
    fmt: dict[str, object] = {}
    if paragraph.style is not None and paragraph.style.name:
        fmt["style_name"] = paragraph.style.name
    if pf.alignment is not None:
        fmt["alignment"] = pf.alignment.name
    if pf.line_spacing is not None:
        fmt["line_spacing"] = pf.line_spacing
    if pf.line_spacing_rule is not None:
        fmt["line_spacing_rule"] = pf.line_spacing_rule.name
    if pf.space_before is not None:
        fmt["space_before"] = pf.space_before.pt
    if pf.space_after is not None:
        fmt["space_after"] = pf.space_after.pt
    if pf.left_indent is not None:
        fmt["left_indent"] = pf.left_indent.pt
    if pf.right_indent is not None:
        fmt["right_indent"] = pf.right_indent.pt
    if pf.first_line_indent is not None:
        fmt["first_line_indent"] = pf.first_line_indent.pt
    if pf.page_break_before is not None:
        fmt["page_break_before"] = pf.page_break_before
    if pf.keep_together is not None:
        fmt["keep_lines_together"] = pf.keep_together
    if pf.keep_with_next is not None:
        fmt["keep_with_next"] = pf.keep_with_next
    return fmt


def extract_list_info(paragraph: Paragraph) -> Optional[dict[str, object]]:
    """Detect list numbering on a paragraph via ``w:numPr``."""
    pPr = paragraph._element.pPr
    if pPr is None:
        return None
    numPr = pPr.find(qn("w:numPr"))
    if numPr is None:
        return None
    numId_el = numPr.find(qn("w:numId"))
    ilvl_el = numPr.find(qn("w:ilvl"))
    if numId_el is None:
        return None
    num_id = int(numId_el.get(qn("w:val")) or "0")
    level = int(ilvl_el.get(qn("w:val")) or "0") if ilvl_el is not None else 0
    return {"num_id": num_id, "level": level}


def resolve_list_is_ordered(document: DocumentObject, num_id: int) -> bool:
    """Look up a numbering definition to determine ordered vs unordered."""
    try:
        numbering_part = document.part.numbering_part
        numbering_el = numbering_part._element
    except (AttributeError, KeyError):
        return False
    num_el = numbering_el.find(
        f'{{http://schemas.openxmlformats.org/wordprocessingml/2006/main}}num'
        f'[@{{http://schemas.openxmlformats.org/wordprocessingml/2006/main}}numId="{num_id}"]'
    )
    if num_el is None:
        return False
    abstract_num_id_el = num_el.find(qn("w:abstractNumId"))
    if abstract_num_id_el is None:
        return False
    abstract_num_id = abstract_num_id_el.get(qn("w:val"))
    abstract_el = numbering_el.find(
        f'{{http://schemas.openxmlformats.org/wordprocessingml/2006/main}}abstractNum'
        f'[@{{http://schemas.openxmlformats.org/wordprocessingml/2006/main}}abstractNumId="{abstract_num_id}"]'
    )
    if abstract_el is None:
        return False
    lvl0 = abstract_el.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}lvl[@{http://schemas.openxmlformats.org/wordprocessingml/2006/main}ilvl="0"]')
    if lvl0 is None:
        lvl0 = abstract_el.find(qn("w:lvl"))
    if lvl0 is None:
        return False
    num_fmt_el = lvl0.find(qn("w:numFmt"))
    if num_fmt_el is None:
        return False
    fmt_val = num_fmt_el.get(qn("w:val")) or ""
    return fmt_val != "bullet"


def extract_paragraph_block(paragraph: Paragraph, *, index: int) -> DocBlock:
    """Normalize a paragraph-like object into a heading or paragraph block."""
    style_name = paragraph.style.name if paragraph.style is not None else None
    heading_level = extract_heading_level(paragraph)
    image_rel_ids = extract_image_relation_ids(paragraph)

    runs = extract_runs_from_paragraph(paragraph)
    hyperlinks = extract_hyperlinks_from_paragraph(paragraph)
    para_format = extract_paragraph_format(paragraph)
    list_info = extract_list_info(paragraph)

    common_meta: dict[str, object] = {
        "index": index,
        "style": style_name,
        "image_rel_ids": image_rel_ids,
        "runs": runs,
        "hyperlinks": hyperlinks,
        "paragraph_format": para_format,
    }
    if list_info is not None:
        common_meta["list_info"] = list_info

    if heading_level is not None:
        return DocBlock(
            type=BlockType.HEADING,
            text=paragraph.text.strip(),
            level=heading_level,
            meta={**common_meta},
        )

    return DocBlock(
        type=BlockType.PARAGRAPH,
        text=paragraph.text.strip(),
        level=0,
        meta={**common_meta},
    )


def extract_table_block(table: Table, *, index: int) -> DocBlock:
    """Normalize a table object into a serializable table block."""
    # Extract cell data with merge info
    table_rows: list[list[dict[str, object]]] = []
    for row in table.rows:
        row_cells: list[dict[str, object]] = []
        for cell in row.cells:
            cell_data: dict[str, object] = {"text": cell.text}
            # Horizontal merge
            gs = getattr(cell, "grid_span", 1)
            if gs > 1:
                cell_data["grid_span"] = gs
            # Vertical merge
            vmerge = cell._tc.vMerge if hasattr(cell._tc, "vMerge") else None
            if vmerge is not None:
                cell_data["v_merge"] = str(vmerge)
            row_cells.append(cell_data)
        table_rows.append(row_cells)

    # Extract column widths
    column_widths: list[float] = []
    try:
        for col in table.columns:
            column_widths.append(col.width)
    except Exception:
        pass

    # Extract table style name
    table_style: Optional[str] = None
    try:
        if table.style is not None and table.style.name:
            table_style = table.style.name
    except Exception:
        pass

    meta: dict[str, object] = {
        "index": index,
        "rows": [[c["text"] for c in row] for row in table_rows],
        "cells": table_rows,
        "row_count": len(table_rows),
        "column_count": max((len(row) for row in table_rows), default=0),
    }
    if column_widths:
        meta["column_widths"] = column_widths
    if table_style:
        meta["table_style"] = table_style

    return DocBlock(
        type=BlockType.TABLE,
        text=None,
        level=0,
        meta=meta,
    )


def _extract_blocks_from_body(body_el, document: DocumentObject, offset: int = 0) -> List[DocBlock]:
    """Extract blocks from an XML body element (document body, header, footer)."""
    blocks: List[DocBlock] = []
    for index, child in enumerate(body_el.iterchildren()):
        if isinstance(child, CT_P):
            para = Paragraph(child, document)
            blocks.append(extract_paragraph_block(para, index=offset + index))
        elif isinstance(child, CT_Tbl):
            tbl = Table(child, document)
            blocks.append(extract_table_block(tbl, index=offset + index))
    return blocks


def extract_blocks(document: DocumentObject) -> List[DocBlock]:
    """Extract a document body into ArborDoc's linear block representation."""
    return _extract_blocks_from_body(document.element.body, document)


def _extract_story_blocks(story, document: DocumentObject, block_type: BlockType, meta_extra: dict) -> List[DocBlock]:
    """Extract paragraphs and tables from a header or footer story."""
    blocks: List[DocBlock] = []
    body_el = story._element
    for index, child in enumerate(body_el.iterchildren()):
        tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
        if tag == "p":
            para = Paragraph(child, document)
            block = extract_paragraph_block(para, index=index)
            block.type = block_type
            block.meta.update(meta_extra)
            blocks.append(block)
        elif tag == "tbl":
            tbl = Table(child, document)
            block = extract_table_block(tbl, index=index)
            block.type = block_type
            block.meta.update(meta_extra)
            blocks.append(block)
    return blocks


def extract_headers_footers(document: DocumentObject) -> List[DocBlock]:
    """Extract all headers and footers from document sections."""
    blocks: List[DocBlock] = []
    for s_idx, section in enumerate(document.sections):
        base_meta = {"section_index": s_idx}

        header = section.header
        if header and not header.is_linked_to_previous:
            blocks.extend(
                _extract_story_blocks(
                    header, document, BlockType.HEADER,
                    {**base_meta, "header_type": "default"},
                )
            )

        if section.different_first_page_header_footer:
            first_header = section.first_page_header
            if first_header:
                blocks.extend(
                    _extract_story_blocks(
                        first_header, document, BlockType.HEADER,
                        {**base_meta, "header_type": "first"},
                    )
                )

        footer = section.footer
        if footer and not footer.is_linked_to_previous:
            blocks.extend(
                _extract_story_blocks(
                    footer, document, BlockType.FOOTER,
                    {**base_meta, "header_type": "default"},
                )
            )

        if section.different_first_page_header_footer:
            first_footer = section.first_page_footer
            if first_footer:
                blocks.extend(
                    _extract_story_blocks(
                        first_footer, document, BlockType.FOOTER,
                        {**base_meta, "header_type": "first"},
                    )
                )

    return blocks


def extract_section_properties(document: DocumentObject) -> list[dict[str, object]]:
    """Read section-level properties from all document sections."""
    sections: list[dict[str, object]] = []
    for section in document.sections:
        sec: dict[str, object] = {}
        sec["page_width"] = section.page_width
        sec["page_height"] = section.page_height
        sec["orientation"] = str(section.orientation)
        sec["left_margin"] = section.left_margin
        sec["right_margin"] = section.right_margin
        sec["top_margin"] = section.top_margin
        sec["bottom_margin"] = section.bottom_margin
        sec["different_first_page"] = section.different_first_page_header_footer
        if section.start_type is not None:
            sec["start_type"] = str(section.start_type)
        sections.append(sec)
    return sections


def extract_all(document: DocumentObject) -> tuple[List[DocBlock], dict[str, object]]:
    """Extract body blocks, headers/footers, and section properties."""
    body_blocks = extract_blocks(document)
    hf_blocks = extract_headers_footers(document)
    sections = extract_section_properties(document)
    all_blocks = hf_blocks + body_blocks
    return all_blocks, {"sections": sections}
