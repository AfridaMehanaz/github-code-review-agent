"""Core review logic: build prompts, call LLM, parse structured output.

Output schema (dict):
{
  "summary": str,
  "bugs": [str, ...],
  "security_issues": [str, ...],
  "style_issues": [str, ...],
  "suggestions": [str, ...]
}
"""

import json
import re

from src.llm_client import chat_completion

REVIEW_SCHEMA_KEYS = ["summary", "bugs", "security_issues", "style_issues", "suggestions"]

SYSTEM_PROMPT = (
    "You are a senior code reviewer. Given a code file or diff, analyze it "
    "and return ONLY a JSON object with these exact keys:\n"
    '  "summary": short overall assessment (1-3 sentences)\n'
    '  "bugs": list of strings, logic errors or correctness bugs\n'
    '  "security_issues": list of strings, security vulnerabilities or risks\n'
    '  "style_issues": list of strings, style/readability/convention issues\n'
    '  "suggestions": list of strings, improvement suggestions\n'
    "Use empty lists for categories with nothing to report. "
    "Do not include markdown formatting, code fences, or any text outside the JSON object."
)


def build_prompt(code, filename="unknown"):
    """Build the user message for a review request."""
    return (
        f"Review the following file: {filename}\n\n"
        f"```\n{code}\n```"
    )


def _extract_json(text):
    """Pull a JSON object out of text, tolerating code fences or stray text."""
    text = text.strip()

    # Strip markdown code fences if present
    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fence_match:
        text = fence_match.group(1)

    # If still not pure JSON, find first { ... last }
    if not text.startswith("{"):
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            text = text[start:end + 1]

    return json.loads(text)


def parse_review_response(raw_text):
    """Parse raw LLM output into the review schema dict.

    Raises ValueError if the response cannot be parsed into valid JSON.
    Missing keys are filled with empty defaults.
    """
    data = _extract_json(raw_text)

    if not isinstance(data, dict):
        raise ValueError("Review response is not a JSON object")

    result = {}
    result["summary"] = str(data.get("summary", "")).strip()
    for key in ("bugs", "security_issues", "style_issues", "suggestions"):
        value = data.get(key, [])
        if isinstance(value, str):
            value = [value] if value.strip() else []
        if not isinstance(value, list):
            value = []
        result[key] = [str(item) for item in value]

    return result


def review_code(code, filename="unknown"):
    """Send code to the LLM and return a structured review dict."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_prompt(code, filename)},
    ]
    raw = chat_completion(messages)
    return parse_review_response(raw)


def format_review_markdown(review, filename="unknown"):
    """Render a structured review dict as markdown."""
    lines = [f"# Review: {filename}", "", "## Summary", review.get("summary", "") or "_none_", ""]

    sections = [
        ("Bugs", "bugs"),
        ("Security Issues", "security_issues"),
        ("Style Issues", "style_issues"),
        ("Suggestions", "suggestions"),
    ]
    for title, key in sections:
        items = review.get(key, [])
        lines.append(f"## {title}")
        if items:
            lines.extend(f"- {item}" for item in items)
        else:
            lines.append("_none_")
        lines.append("")

    return "\n".join(lines)
