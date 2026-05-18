from arbordoc.converters.latex import LatexExporter
from arbordoc.core.parser import parse_docx


def test_latex_exporter_renders_baseline_tree(sample_source_docx) -> None:
    root = parse_docx(sample_source_docx)
    rendered = LatexExporter().export(root)

    assert r"\documentclass{article}" in rendered
    assert r"\section{Main Title}" in rendered
    assert "Intro paragraph." in rendered
    assert r"\subsection{Section A}" in rendered
    assert "Section body." in rendered
    assert r"\begin{tabular}{|l|l|}" in rendered
    assert "A1 & B1" in rendered


def test_latex_exporter_supports_fragment_mode(sample_source_docx) -> None:
    root = parse_docx(sample_source_docx)
    rendered = LatexExporter(standalone=False).export(root)

    assert r"\documentclass{article}" not in rendered
    assert r"\begin{document}" not in rendered
    assert r"\section{Main Title}" in rendered
