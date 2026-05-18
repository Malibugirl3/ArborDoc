"""Minimal LaTeX exporter for ArborDoc trees.

Phase 2 can evolve this module toward high-fidelity conversion. This first
version focuses on a predictable, testable baseline:
- heading levels map to section commands
- paragraphs become plain text blocks
- tables become simple bordered tabular environments
- images become TODO placeholders with relationship ids
"""

from __future__ import annotations

from arbordoc.converters.base import BaseExporter
from arbordoc.models.schema import DocNode, HyperlinkRun, InlineImageInline, NodeType, TextRun

_ESCAPE_MAP = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}


def _escape_latex(text: str) -> str:
    escaped = text
    for source, target in _ESCAPE_MAP.items():
        escaped = escaped.replace(source, target)
    return escaped


class LatexExporter(BaseExporter):
    """Convert a DocTree into a basic LaTeX document string."""

    def __init__(self, *, standalone: bool = True) -> None:
        self.standalone = standalone

    def export(self, root: DocNode) -> str:
        lines: list[str] = []
        if self.standalone:
            lines.extend(
                [
                    r"\documentclass{article}",
                    r"\usepackage[utf8]{inputenc}",
                    r"\usepackage{array}",
                    r"\begin{document}",
                    "",
                ]
            )

        for child in root.children:
            lines.extend(self._render_node(child))

        if self.standalone:
            lines.extend(["", r"\end{document}"])
        return "\n".join(lines).rstrip() + "\n"

    def _render_inline(self, node: DocNode) -> str:
        """Render inline_content into LaTeX, falling back to plain text."""
        inline = node.inline_content
        if not inline:
            return _escape_latex((node.text or "").strip())

        parts: list[str] = []
        for element in inline:
            if isinstance(element, TextRun):
                text = _escape_latex(element.text)
                fmt = element.format
                if fmt.bold:
                    text = f"\\textbf{{{text}}}"
                if fmt.italic:
                    text = f"\\textit{{{text}}}"
                if fmt.underline:
                    text = f"\\underline{{{text}}}"
                if fmt.strikethrough:
                    text = f"\\sout{{{text}}}"
                if fmt.superscript:
                    text = f"\\textsuperscript{{{text}}}"
                if fmt.subscript:
                    text = f"\\textsubscript{{{text}}}"
                parts.append(text)
            elif isinstance(element, HyperlinkRun):
                url = _escape_latex(element.url)
                child_text = "".join(_escape_latex(c.text) for c in element.children)
                parts.append(f"\\href{{{url}}}{{{child_text}}}")
            elif isinstance(element, InlineImageInline):
                rid = _escape_latex(element.relationship_id)
                parts.append(f"% TODO: inline image rId={rid}")

        return "".join(parts) if parts else _escape_latex((node.text or "").strip())

    def _render_node(self, node: DocNode) -> list[str]:
        if node.type == NodeType.HEADING:
            return self._render_heading(node)
        if node.type == NodeType.PARAGRAPH:
            text = self._render_inline(node)
            if not text:
                return []
            return [text, ""]
        if node.type == NodeType.TABLE:
            return self._render_table(node)
        if node.type == NodeType.IMAGE:
            rel_id = _escape_latex(node.meta.get("relationship_id", "unknown"))
            return [f"% TODO: embedded image relationship id = {rel_id}", ""]
        return []

    def _render_heading(self, node: DocNode) -> list[str]:
        command = self._heading_command(node.level)
        title = self._render_inline(node)
        lines = [f"{command}{{{title}}}", ""]
        for child in node.children:
            lines.extend(self._render_node(child))
        return lines

    def _render_table(self, node: DocNode) -> list[str]:
        rows = node.meta.get("rows", [])
        if not rows:
            return [r"\begin{tabular}{|l|}", r"\hline", r"\end{tabular}", ""]

        column_count = int(node.meta.get("column_count", 0)) or max(len(r) for r in rows)
        spec = "|" + "|".join("l" for _ in range(column_count)) + "|"

        lines = [rf"\begin{{tabular}}{{{spec}}}", r"\hline"]
        for row in rows:
            padded = list(row) + [""] * max(column_count - len(row), 0)
            escaped_cells = [_escape_latex(str(cell)) for cell in padded[:column_count]]
            lines.append(" & ".join(escaped_cells) + r" \\")
            lines.append(r"\hline")
        lines.extend([r"\end{tabular}", ""])
        return lines

    @staticmethod
    def _heading_command(level: int) -> str:
        if level <= 1:
            return r"\section"
        if level == 2:
            return r"\subsection"
        if level == 3:
            return r"\subsubsection"
        return r"\paragraph"
