"""Transaction classification rules."""

from __future__ import annotations

from collections.abc import Iterable

RULES_BY_CATEGORY: dict[str, tuple[str, ...]] = {
    "Food": ("starbucks", "mcdonalds"),
    "Subscription": ("netflix", "spotify"),
    "Shopping": ("amazon", "walmart"),
}
DEFAULT_CATEGORY = "Uncategorized"


def classify_transaction(description: str, categories_order: Iterable[str] | None = None) -> str:
    """Classify a transaction description into a known category."""
    normalized_description = description.strip().lower()
    if not normalized_description:
        return DEFAULT_CATEGORY

    candidate_categories = tuple(categories_order) if categories_order else tuple(RULES_BY_CATEGORY.keys())
    for category in candidate_categories:
        for keyword in RULES_BY_CATEGORY.get(category, ()):
            if keyword in normalized_description:
                return category

    return DEFAULT_CATEGORY
