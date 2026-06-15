# GitHub Code Review Agent

LLM-powered code review agent. Reads a code file or diff and outputs a
structured review: bugs, security issues, style issues, and suggestions.

**No GitHub write access.** Read-only — analyzes local files (`samples/` or
pasted code) and returns a structured report. Does not post comments,
open PRs, or touch any repo.

## Features

- Provider-agnostic LLM client (OpenAI-compatible API: Groq, OpenAI, etc.)
- Structured JSON output: `summary`, `bugs`, `security_issues`, `style_issues`, `suggestions`
- Streamlit UI for interactive review
- Pytest suite for parsing/formatting logic — runs without an API key

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env, set LLM_API_KEY=<your real key>
```

Default config targets Groq (`llama-3.3-70b-versatile`,
`https://api.groq.com/openai/v1`). Swap `LLM_BASE_URL` / `LLM_MODEL` in `.env`
for any OpenAI-compatible provider.

## Usage

### Streamlit UI

```bash
streamlit run app.py
```

Pick a file from `samples/` or paste code, click review, get a structured
breakdown with a downloadable markdown report.

### Programmatic

```python
from src.reviewer import review_code

with open("samples/buggy_calculator.py") as f:
    code = f.read()

result = review_code(code, filename="buggy_calculator.py")
print(result["summary"])
print(result["security_issues"])
```

## Tests

```bash
pytest
```

Tests cover prompt building and response parsing/formatting — no API key
or network calls required.

## Project structure

```
github-code-review-agent/
  app.py              # Streamlit UI
  src/
    llm_client.py      # provider-agnostic OpenAI-compatible client
    reviewer.py         # prompt building, response parsing, formatting
  tests/
    test_reviewer.py    # pytest suite (no API key needed)
  samples/              # example files for demo review
  .env.example
  requirements.txt
```
