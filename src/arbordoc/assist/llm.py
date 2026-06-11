"""DeepSeek LLM adapter for the ArborDoc assist pipeline.

This module calls the DeepSeek API (OpenAI-compatible) to analyse a parsed
document's structural review and return human-readable suggestions.
"""

from __future__ import annotations

from typing import Optional

from arbordoc.assist.review import build_assist_review_markdown
from arbordoc.models.schema import DocNode

DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"

SYSTEM_PROMPT = """\
You are a document structure analysis expert. You receive a structural review \
of a parsed Word document (in Markdown format). The review contains an outline \
and any structural issues that were automatically detected.

Your task is to provide a concise, actionable analysis covering:

1. **Structural Issues**: Confirm or rebut each issue from the review.
2. **Suggested Fixes**: For each issue, suggest a concrete fix.
3. **Overall Assessment**: A 1-3 sentence summary of document quality.
4. **Tips**: Any other structural improvements.

Be concise. Use plain text or simple Markdown. Do NOT output JSON."""

USER_PROMPT_TEMPLATE = """\
## Document Structural Review

{review_md}

Analyse the document structure above. Provide your analysis following the \
four sections: Structural Issues, Suggested Fixes, Overall Assessment, Tips."""


def build_analysis_prompt(review_md: str) -> str:
    """Build the user prompt from the structural review only."""
    truncated = review_md[:8000]
    if len(review_md) > 8000:
        truncated += "\n\n... (review truncated)\n"
    return USER_PROMPT_TEMPLATE.format(review_md=truncated)


def call_deepseek(
    system: str,
    user: str,
    *,
    api_key: str,
    model: str = DEEPSEEK_MODEL,
    base_url: str = DEEPSEEK_BASE_URL,
) -> str:
    """Call the DeepSeek API and return the assistant message text."""
    from openai import OpenAI

    client = OpenAI(api_key=api_key, base_url=base_url)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.3,
        max_tokens=4096,
    )
    content = response.choices[0].message.content
    return content.strip() if content else ""


def analyse_with_llm(
    tree: DocNode,
    api_key: Optional[str] = None,
) -> tuple[str, str]:
    """Analyse a document tree with DeepSeek and return text analysis.

    Returns:
        (review_md, ai_analysis) — both Markdown strings.
    """
    if not api_key:
        raise ValueError("DeepSeek API key is required for LLM analysis.")

    review_md = build_assist_review_markdown(tree)
    user_prompt = build_analysis_prompt(review_md)

    ai_analysis = call_deepseek(SYSTEM_PROMPT, user_prompt, api_key=api_key)

    if not ai_analysis:
        raise RuntimeError("DeepSeek returned an empty response.")

    return review_md, ai_analysis
