import json
import pytest

from src.reviewer import (
    build_prompt,
    parse_review_response,
    format_review_markdown,
    REVIEW_SCHEMA_KEYS,
)


def test_build_prompt_includes_filename_and_code():
    prompt = build_prompt("print('hi')", filename="foo.py")
    assert "foo.py" in prompt
    assert "print('hi')" in prompt


def test_parse_review_response_clean_json():
    raw = json.dumps({
        "summary": "Looks fine.",
        "bugs": ["off-by-one in loop"],
        "security_issues": [],
        "style_issues": ["use snake_case"],
        "suggestions": ["add type hints"],
    })
    result = parse_review_response(raw)

    assert result["summary"] == "Looks fine."
    assert result["bugs"] == ["off-by-one in loop"]
    assert result["security_issues"] == []
    assert result["style_issues"] == ["use snake_case"]
    assert result["suggestions"] == ["add type hints"]
    assert set(result.keys()) == set(REVIEW_SCHEMA_KEYS)


def test_parse_review_response_with_code_fence():
    raw = "```json\n" + json.dumps({"summary": "ok", "bugs": [], "security_issues": [],
                                     "style_issues": [], "suggestions": []}) + "\n```"
    result = parse_review_response(raw)
    assert result["summary"] == "ok"


def test_parse_review_response_with_stray_text():
    raw = "Here is the review:\n" + json.dumps({
        "summary": "ok", "bugs": ["bug1"], "security_issues": [],
        "style_issues": [], "suggestions": []
    }) + "\nHope that helps!"
    result = parse_review_response(raw)
    assert result["bugs"] == ["bug1"]


def test_parse_review_response_missing_keys_default_empty():
    raw = json.dumps({"summary": "partial"})
    result = parse_review_response(raw)
    assert result["bugs"] == []
    assert result["security_issues"] == []
    assert result["style_issues"] == []
    assert result["suggestions"] == []


def test_parse_review_response_coerces_string_to_list():
    raw = json.dumps({"summary": "ok", "bugs": "single bug as string",
                       "security_issues": [], "style_issues": [], "suggestions": []})
    result = parse_review_response(raw)
    assert result["bugs"] == ["single bug as string"]


def test_parse_review_response_invalid_json_raises():
    with pytest.raises(ValueError):
        parse_review_response("not json at all")


def test_format_review_markdown_contains_sections():
    review = {
        "summary": "All good",
        "bugs": ["bug a"],
        "security_issues": [],
        "style_issues": ["style a"],
        "suggestions": ["suggestion a"],
    }
    md = format_review_markdown(review, filename="bar.py")

    assert "# Review: bar.py" in md
    assert "## Summary" in md
    assert "All good" in md
    assert "- bug a" in md
    assert "## Security Issues" in md
    assert "_none_" in md
    assert "- style a" in md
    assert "- suggestion a" in md
