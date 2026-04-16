"""Rule-based transaction description classifier.

The implementation is intentionally rule-based for the first PoC round: the
rules are data-driven so an LLM-backed implementation can later be swapped in
without changing the public ``classify_transaction`` signature.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from enum import StrEnum


class Category(StrEnum):
    """Known transaction categories."""

    FOOD = "Food"
    SUBSCRIPTION = "Subscription"
    SHOPPING = "Shopping"
    TRANSPORT = "Transport"
    SALARY = "Salary"
    UNCATEGORIZED = "Uncategorized"


CATEGORY_RULES: dict[Category, tuple[str, ...]] = {
    Category.FOOD: ("starbucks", "mcdonalds", "chipotle", "dominos", "uber eats", "doordash"),
    Category.SUBSCRIPTION: ("netflix", "spotify", "hulu", "disney+", "hbo", "prime video"),
    Category.SHOPPING: ("amazon", "walmart", "target", "ebay", "ikea"),
    Category.TRANSPORT: ("uber", "lyft", "shell", "exxon", "chevron"),
    Category.SALARY: ("payroll", "salary", "direct deposit"),
}


_WHITESPACE_RE = re.compile(r"\s+")


def sanitize_description(description: str) -> str:
    """Normalize a raw bank description for matching.

    Strips surrounding whitespace, collapses internal whitespace, and lowercases
    so keyword matching is order-insensitive and tolerant of noisy inputs such
    as ``"  NETFLIX.COM   BILL "``.
    """
    return _WHITESPACE_RE.sub(" ", description or "").strip().lower()


def _match(cleaned: str, keywords: Iterable[str]) -> bool:
    return any(keyword in cleaned for keyword in keywords)


def classify_transaction(description: str) -> str:
    """Classify a raw transaction description into a :class:`Category`.

    Returns the string value of the matching :class:`Category`. Falls back to
    :pyattr:`Category.UNCATEGORIZED` when no rule matches.
    """
    cleaned = sanitize_description(description)
    if not cleaned:
        return Category.UNCATEGORIZED.value

    for category, keywords in CATEGORY_RULES.items():
        if _match(cleaned, keywords):
            return category.value

    return Category.UNCATEGORIZED.value
