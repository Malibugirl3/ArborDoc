"""Human-readable structural review (local rules, no LLM required)."""

from __future__ import annotations

from typing import List, Optional

from arbordoc.core.tree import walk_depth_first
from arbordoc.models.schema import DocNode, NodeType


def build_assist_review_markdown(root: DocNode) -> str:
    """Build a Markdown document editors can read before any merge or transform."""
    lines: List[str] = [
        "# ArborDoc assist review",
        "",
        "This report is generated locally from the parsed document tree.",
        "LLM-assisted proposals are optional and must not silently overwrite your tree.",
        "",
        "## Outline",
        "",
    ]

    prev_heading_level: Optional[int] = None
    issues: List[str] = []

    for node in walk_depth_first(root, skip_root=True):
        if node.type == NodeType.HEADING:
            indent = "  " * max(node.level - 1, 0)
            title = (node.text or "").strip() or "(empty heading)"
            lines.append(f"{indent}- H{node.level}: {title}")
            if not (node.text or "").strip():
                issues.append(f"Empty heading at level H{node.level}.")
            if prev_heading_level is not None and node.level > prev_heading_level + 1:
                issues.append(
                    f"Possible outline skip: after H{prev_heading_level} "
                    f"saw H{node.level} ('{title}')."
                )
            prev_heading_level = node.level

    lines.extend(["", "## Structural checks", ""])

    if not issues:
        lines.append("- No obvious structural warnings.")
    else:
        for item in issues:
            lines.append(f"- {item}")

    lines.extend(
        [
            "",
            "## Next steps",
            "",
            "- Inspect `tree.base.json` (baseline snapshot).",
            "- If you add `tree.proposed.json`, set `merge_instructions.json` to `\"tree_source\": \"proposed\"`.",
            "- Run `arbordoc assist apply --workspace ...` only after you agree with the instructions.",
            "",
        ]
    )

    return "\n".join(lines)
