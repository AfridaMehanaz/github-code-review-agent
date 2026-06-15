"""Sample file with relatively clean code for contrast."""

from __future__ import annotations


def safe_divide(a: float, b: float) -> float | None:
    """Return a / b, or None if b is zero."""
    if b == 0:
        return None
    return a / b


def average(numbers: list[float]) -> float:
    """Return the arithmetic mean. Raises ValueError on empty input."""
    if not numbers:
        raise ValueError("numbers must not be empty")
    return sum(numbers) / len(numbers)


def read_text_file(path: str) -> str:
    """Read and return file contents, ensuring the handle is closed."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
