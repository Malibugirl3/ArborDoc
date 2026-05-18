import json

from arbordoc.cli import main


def test_cli_parse_writes_json(sample_source_docx, tmp_path) -> None:
    output_path = tmp_path / "parsed.json"

    exit_code = main(["parse", "-i", str(sample_source_docx), "-o", str(output_path)])

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert exit_code == 0
    assert payload["type"] == "document"
    assert payload["children"][0]["text"] == "Main Title"


def test_cli_export_latex_writes_tex(sample_source_docx, tmp_path) -> None:
    output_path = tmp_path / "output.tex"

    exit_code = main(["export-latex", "-i", str(sample_source_docx), "-o", str(output_path)])

    rendered = output_path.read_text(encoding="utf-8")
    assert exit_code == 0
    assert r"\section{Main Title}" in rendered
    assert r"\subsection{Section A}" in rendered
    assert r"\begin{tabular}" in rendered
