"""Minimal template reconstruction helpers for ArborDoc.

This module sits above the parser/tree layer:
- parser: turns low-level DOCX content into ArborDoc's DocTree
- styler: takes DocTree and writes supported content back into a document

That separation keeps parsing rules and output rules independent.
"""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Union, cast

from docx import Document
from docx.document import Document as DocumentObject
from docx.shared import Inches

from arbordoc.core.extractor import extract_image_blob_cache
from arbordoc.core.parser import parse_docx
from arbordoc.core.tree import walk_depth_first
from arbordoc.models.schema import DocNode, NodeType

DEFAULT_STYLE_MAP = {
    "paragraph": "Normal",
}

DEFAULT_IMAGE_RENDER_WIDTH = Inches(4)


def _table_rows_as_matrix(rows: object) -> List[List[str]]:
    """Flatten cell values from parser meta into rectangular text rows."""
    if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes)):
        return []

    normalized: List[List[str]] = []
    for row in rows:
        if isinstance(row, Sequence) and not isinstance(row, (str, bytes)):
            normalized.append([str(cell) if cell is not None else "" for cell in cast(Sequence[object], row)])
        else:
            normalized.append(["" if row is None else str(row)])

    width = max((len(row) for row in normalized), default=0)
    for row in normalized:
        if len(row) < width:
            row.extend([""] * (width - len(row)))
    return normalized


def _append_table(document: DocumentObject, meta: Mapping[str, object]) -> None:
    rows = _table_rows_as_matrix(meta.get("rows"))
    if not rows:
        table = document.add_table(rows=1, cols=1)
        table.cell(0, 0).text = ""
        return

    nrows = len(rows)
    ncols = len(rows[0])
    table = document.add_table(rows=nrows, cols=ncols)

    for i, row in enumerate(rows):
        for j in range(ncols):
            table.cell(i, j).text = row[j]


def _append_image(
    document: DocumentObject,
    blob: bytes,
) -> None:
    paragraph = document.add_paragraph()
    paragraph.add_run().add_picture(
        BytesIO(blob),
        width=DEFAULT_IMAGE_RENDER_WIDTH,
    )


def _clear_document_body(document: DocumentObject) -> None:
    """Remove existing body content while keeping section settings intact."""
    body = document._element.body
    for child in list(body):
        if child.tag.endswith("sectPr"):
            continue
        body.remove(child)


def _safe_apply_style(paragraph, style_name: str) -> None:
    try:
        paragraph.style = style_name
    except (KeyError, ValueError):
        return


def _heading_style_name(level: int, style_map: Dict[str, str]) -> str:
    return style_map.get(f"heading.{level}") or style_map.get("heading") or f"Heading {level}"


def render_tree_to_template(
    root: DocNode,
    template_path: Union[str, Path],
    output_path: Union[str, Path],
    *,
    style_map: Optional[Dict[str, str]] = None,
    source_path: Optional[Union[str, Path]] = None,
) -> Path:
    """Render supported nodes into a template-driven DOCX document.

    When ``source_path`` matches the original DOCX that produced ``root``, IMAGE nodes whose
    ``meta`` exposes ``relationship_id`` can reuse embedded image blobs.
    """
    template = Path(template_path)
    output = Path(output_path)
    document = Document(template)
    resolved_style_map = {**DEFAULT_STYLE_MAP, **(style_map or {})}

    image_blob_cache: Dict[str, bytes] = {}
    if source_path is not None:
        src = Document(Path(source_path))
        image_blob_cache = extract_image_blob_cache(src)

    _clear_document_body(document)

    skipped_nodes: List[str] = []
    for node in walk_depth_first(root, skip_root=True):
        if node.type == NodeType.HEADING:
            paragraph = document.add_paragraph(node.text or "")
            _safe_apply_style(paragraph, _heading_style_name(max(node.level, 1), resolved_style_map))
        elif node.type == NodeType.PARAGRAPH:
            paragraph = document.add_paragraph(node.text or "")
            _safe_apply_style(paragraph, resolved_style_map["paragraph"])
        elif node.type == NodeType.TABLE:
            meta = cast(Mapping[str, object], node.meta)
            _append_table(document, meta)
        elif node.type == NodeType.IMAGE:
            rid_raw = node.meta.get("relationship_id")
            blob: Optional[bytes] = None
            if isinstance(rid_raw, str):
                blob = image_blob_cache.get(rid_raw)
            if blob is not None:
                _append_image(document, blob)
            else:
                skipped_nodes.append(
                    "image:no_blob_or_source"
                    if not source_path
                    else f"image:missing_rid={rid_raw}"
                )

    if skipped_nodes:
        document.core_properties.comments = (
            "Skipped unsupported nodes during render: " + ", ".join(sorted(set(skipped_nodes)))
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    document.save(output)
    return output


def transform_docx(
    input_path: Union[str, Path],
    template_path: Union[str, Path],
    output_path: Union[str, Path],
    *,
    style_map: Optional[Dict[str, str]] = None,
) -> Path:
    """Parse a source document and render supported nodes into a template."""
    root = parse_docx(input_path)
    return render_tree_to_template(
        root,
        template_path,
        output_path,
        style_map=style_map,
        source_path=input_path,
    )
