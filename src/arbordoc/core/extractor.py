"""DOCX extraction helpers that normalize `python-docx` objects into blocks.

This module is ArborDoc's boundary with the low-level dependency layer:
- `python-docx` reads OOXML-backed document objects
- extractor functions translate those objects into ArborDoc `DocBlock`s
- higher layers can then parse blocks without depending on raw DOCX objects
"""

from __future__ import annotations

import re
from typing import Iterator, List, Optional, Union

from docx.document import Document as DocumentObject
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


def extract_paragraph_block(paragraph: Paragraph, *, index: int) -> DocBlock:
    """Normalize a paragraph-like object into a heading or paragraph block."""
    style_name = paragraph.style.name if paragraph.style is not None else None
    heading_level = extract_heading_level(paragraph)
    image_rel_ids = extract_image_relation_ids(paragraph)

    if heading_level is not None:
        return DocBlock(
            type=BlockType.HEADING,
            text=paragraph.text.strip(),
            level=heading_level,
            meta={
                "index": index,
                "style": style_name,
                "image_rel_ids": image_rel_ids,
            },
        )

    return DocBlock(
        type=BlockType.PARAGRAPH,
        text=paragraph.text.strip(),
        level=0,
        meta={
            "index": index,
            "style": style_name,
            "image_rel_ids": image_rel_ids,
        },
    )


def extract_table_block(table: Table, *, index: int) -> DocBlock:
    """Normalize a table object into a serializable table block."""
    rows = [[cell.text for cell in row.cells] for row in table.rows]
    column_count = max((len(row) for row in rows), default=0)
    return DocBlock(
        type=BlockType.TABLE,
        text=None,
        level=0,
        meta={
            "index": index,
            "rows": rows,
            "row_count": len(rows),
            "column_count": column_count,
        },
    )


def extract_blocks(document: DocumentObject) -> List[DocBlock]:
    """Extract a document into ArborDoc's linear block representation."""
    blocks: List[DocBlock] = []

    for index, block in enumerate(iter_block_items(document)):
        if isinstance(block, Paragraph):
            blocks.append(extract_paragraph_block(block, index=index))
            continue

        blocks.append(extract_table_block(block, index=index))

    return blocks
