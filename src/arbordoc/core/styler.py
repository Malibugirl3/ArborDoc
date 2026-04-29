"""Minimal template reconstruction helpers for ArborDoc.

This module sits above the parser/tree layer:
- parser: turns low-level DOCX content into ArborDoc's DocTree
- styler: takes DocTree and writes supported content back into a document

That separation keeps parsing rules and output rules independent.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Union

from docx import Document
from docx.document import Document as DocumentObject

from arbordoc.core.parser import parse_docx
from arbordoc.core.tree import walk_depth_first
from arbordoc.models.schema import DocNode, NodeType

DEFAULT_STYLE_MAP = {
    "paragraph": "Normal",
}


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
) -> Path:
    """Render supported nodes into a template-driven DOCX document."""
    template = Path(template_path)
    output = Path(output_path)
    document = Document(template)
    resolved_style_map = {**DEFAULT_STYLE_MAP, **(style_map or {})}

    _clear_document_body(document)

    skipped_nodes: List[str] = []
    for node in walk_depth_first(root, skip_root=True):
        if node.type == NodeType.HEADING:
            paragraph = document.add_paragraph(node.text or "")
            _safe_apply_style(paragraph, _heading_style_name(max(node.level, 1), resolved_style_map))
        elif node.type == NodeType.PARAGRAPH:
            paragraph = document.add_paragraph(node.text or "")
            _safe_apply_style(paragraph, resolved_style_map["paragraph"])
        elif node.type in {NodeType.TABLE, NodeType.IMAGE}:
            # Phase 1 rebuild is intentionally conservative:
            # unsupported nodes are recorded rather than guessed.
            skipped_nodes.append(node.type.value)

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
    return render_tree_to_template(root, template_path, output_path, style_map=style_map)
