from __future__ import annotations

from pathlib import Path

import pytest
from docx import Document


@pytest.fixture()
def sample_source_docx(tmp_path: Path) -> Path:
    path = tmp_path / "source.docx"
    document = Document()
    document.add_heading("Main Title", level=1)
    document.add_paragraph("Intro paragraph.")
    document.add_heading("Section A", level=2)
    document.add_paragraph("Section body.")
    table = document.add_table(rows=2, cols=2)
    table.cell(0, 0).text = "A1"
    table.cell(0, 1).text = "B1"
    table.cell(1, 0).text = "A2"
    table.cell(1, 1).text = "B2"
    document.save(path)
    return path


@pytest.fixture()
def sample_template_docx(tmp_path: Path) -> Path:
    path = tmp_path / "template.docx"
    document = Document()
    document.add_paragraph("Template placeholder.")
    document.save(path)
    return path
