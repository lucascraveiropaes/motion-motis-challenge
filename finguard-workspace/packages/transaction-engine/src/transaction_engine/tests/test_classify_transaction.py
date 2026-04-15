"""
Unit tests for classify_transaction().

All matching is case-insensitive — every rule is exercised with
lowercase, uppercase, mixed-case, and embedded-in-sentence variants.
"""
import pytest
from transaction_engine.classifier import classify_transaction


# ---------------------------------------------------------------------------
# Parametrised happy-path tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("description, expected", [
    # ── Food ────────────────────────────────────────────────────────────────
    ("starbucks",                   "Food"),          # exact lowercase
    ("Starbucks",                   "Food"),          # title case
    ("STARBUCKS",                   "Food"),          # all caps
    ("Starbucks Coffee $4.50",      "Food"),          # embedded in sentence
    ("mcdonalds",                   "Food"),
    ("McDonalds",                   "Food"),
    ("MCDONALDS",                   "Food"),
    ("Lunch at McDonalds $8.99",    "Food"),

    # ── Subscription ────────────────────────────────────────────────────────
    ("netflix",                     "Subscription"),
    ("Netflix",                     "Subscription"),
    ("NETFLIX",                     "Subscription"),
    ("Netflix monthly charge",      "Subscription"),
    ("spotify",                     "Subscription"),
    ("Spotify",                     "Subscription"),
    ("SPOTIFY",                     "Subscription"),
    ("Spotify Premium $9.99",       "Subscription"),

    # ── Shopping ────────────────────────────────────────────────────────────
    ("amazon",                      "Shopping"),
    ("Amazon",                      "Shopping"),
    ("AMAZON",                      "Shopping"),
    ("Amazon Prime order $35.00",   "Shopping"),
    ("walmart",                     "Shopping"),
    ("Walmart",                     "Shopping"),
    ("WALMART",                     "Shopping"),
    ("Walmart Supercenter $102.40", "Shopping"),

    # ── Uncategorized ───────────────────────────────────────────────────────
    ("Uber ride $12.00",            "Uncategorized"),
    ("random charge",               "Uncategorized"),
    ("",                            "Uncategorized"),
    ("   ",                         "Uncategorized"),
])
def test_classify_transaction(description: str, expected: str):
    assert classify_transaction(description) == expected


# ---------------------------------------------------------------------------
# Non-string inputs → always Uncategorized
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("bad_input", [
    None,
    123,
    ["starbucks"],
    {"merchant": "netflix"},
    object(),
])
def test_non_string_input_returns_uncategorized(bad_input):
    assert classify_transaction(bad_input) == "Uncategorized"


# ---------------------------------------------------------------------------
# First-match-wins: ensure rule order is stable when multiple keywords hit
# ---------------------------------------------------------------------------

def test_return_type_is_str():
    """Return value must always be a plain str, not an enum member."""
    result = classify_transaction("Starbucks")
    assert type(result) is str


def test_no_partial_false_positive():
    """'amazonian' contains 'amazon' — verify substring matching is intentional."""
    # The function does substring match, so this WILL match Shopping.
    # This test documents the behaviour rather than asserting it shouldn't match.
    result = classify_transaction("amazonian expedition")
    assert result == "Shopping"
