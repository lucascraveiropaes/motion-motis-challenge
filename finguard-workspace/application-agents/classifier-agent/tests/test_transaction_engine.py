"""Extra coverage for the pure transaction-engine package."""

from __future__ import annotations

import pytest
from transaction_engine import Category, classify_transaction, sanitize_description


@pytest.mark.parametrize(
    ("description", "expected"),
    [
        ("Starbucks Coffee", Category.FOOD.value),
        ("NETFLIX.COM BILL", Category.SUBSCRIPTION.value),
        ("Amazon Marketplace", Category.SHOPPING.value),
        ("UBER TRIP 1234", Category.TRANSPORT.value),
        ("ACME CORP PAYROLL", Category.SALARY.value),
        ("Random unknown merchant", Category.UNCATEGORIZED.value),
        ("", Category.UNCATEGORIZED.value),
        ("   ", Category.UNCATEGORIZED.value),
    ],
)
def test_classify_transaction_cases(description: str, expected: str) -> None:
    assert classify_transaction(description) == expected


def test_sanitize_description_collapses_whitespace() -> None:
    assert sanitize_description("  Hello\tWorld\n ") == "hello world"


def test_sanitize_description_handles_empty() -> None:
    assert sanitize_description("") == ""
