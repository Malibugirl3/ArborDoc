from docx import Document

from arbordoc.core.styler import render_tree_to_template, transform_docx
from arbordoc.models.schema import DocNode, NodeType


def test_render_tree_to_template_writes_supported_content(sample_template_docx, tmp_path) -> None:
    root = DocNode(
        type=NodeType.DOCUMENT,
        children=[
            DocNode(type=NodeType.HEADING, level=1, text="Rendered Title"),
            DocNode(type=NodeType.PARAGRAPH, level=1, text="Rendered paragraph"),
            DocNode(type=NodeType.TABLE, level=1, meta={"rows": [["ignored"]]}),
        ],
    )
    output_path = tmp_path / "rendered.docx"

    render_tree_to_template(root, sample_template_docx, output_path)

    document = Document(output_path)
    texts = [paragraph.text for paragraph in document.paragraphs]
    assert texts == ["Rendered Title", "Rendered paragraph"]


def test_transform_docx_creates_output(sample_source_docx, sample_template_docx, tmp_path) -> None:
    output_path = tmp_path / "transformed.docx"

    transform_docx(sample_source_docx, sample_template_docx, output_path)

    document = Document(output_path)
    texts = [paragraph.text for paragraph in document.paragraphs]
    assert "Main Title" in texts
    assert "Intro paragraph." in texts
