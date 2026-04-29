from arbordoc.models.schema import BlockType, DocBlock, DocNode, NodeType


def test_docblock_serializes_linear_content() -> None:
    block = DocBlock(
        type=BlockType.HEADING,
        text="Heading",
        level=1,
        meta={"style": "Heading 1"},
    )

    payload = block.to_dict()

    assert payload["type"] == "heading"
    assert payload["level"] == 1
    assert payload["meta"]["style"] == "Heading 1"


def test_docnode_serializes_nested_children() -> None:
    root = DocNode(type=NodeType.DOCUMENT)
    heading = root.add_child(DocNode(type=NodeType.HEADING, level=1, text="Heading"))
    heading.add_child(DocNode(type=NodeType.PARAGRAPH, level=1, text="Paragraph"))

    payload = root.to_dict()

    assert payload["type"] == "document"
    assert payload["children"][0]["type"] == "heading"
    assert payload["children"][0]["children"][0]["text"] == "Paragraph"
