"""Transaction engine: classification rules and sanitization helpers."""

from transaction_engine.classifier import (
    CATEGORY_RULES,
    Category,
    classify_transaction,
    sanitize_description,
)

__all__ = [
    "CATEGORY_RULES",
    "Category",
    "classify_transaction",
    "sanitize_description",
]
