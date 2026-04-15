"""
Pure business logic for classifying raw transaction strings.
No FastAPI, no DB — just domain logic.
"""
from dataclasses import dataclass
from enum import StrEnum


class TransactionCategory(StrEnum):
    FOOD = "food"
    TRANSPORT = "transport"
    UTILITIES = "utilities"
    ENTERTAINMENT = "entertainment"
    HEALTH = "health"
    SHOPPING = "shopping"
    INCOME = "income"
    TRANSFER = "transfer"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ClassifiedTransaction:
    raw: str
    category: TransactionCategory
    merchant: str | None
    amount: float | None
    confidence: float          # 0.0 – 1.0


# ---------------------------------------------------------------------------
# Keyword-based classifier (swap for ML/LLM call as needed)
# ---------------------------------------------------------------------------

_RULES: list[tuple[list[str], TransactionCategory]] = [
    (["uber", "lyft", "bolt", "taxi", "metro", "transit", "fuel", "shell", "bp"], TransactionCategory.TRANSPORT),
    (["netflix", "spotify", "steam", "cinema", "hbo", "disney"], TransactionCategory.ENTERTAINMENT),
    (["amazon", "zara", "h&m", "ikea", "walmart", "target"], TransactionCategory.SHOPPING),
    (["salary", "payroll", "paycheck", "deposit", "income", "dividend"], TransactionCategory.INCOME),
    (["transfer", "zelle", "venmo", "wire", "remittance"], TransactionCategory.TRANSFER),
    (["electricity", "water", "internet", "broadband", "gas bill", "utility"], TransactionCategory.UTILITIES),
    (["pharmacy", "hospital", "clinic", "dentist", "health", "doctor"], TransactionCategory.HEALTH),
    (["restaurant", "cafe", "starbucks", "mcdonald", "pizza", "sushi", "grubhub", "doordash"], TransactionCategory.FOOD),
]


def _extract_amount(raw: str) -> float | None:
    import re
    match = re.search(r"\$?([\d,]+(?:\.\d{1,2})?)", raw)
    if match:
        return float(match.group(1).replace(",", ""))
    return None


def _extract_merchant(raw: str) -> str | None:
    """Return the first capitalised token that looks like a merchant name."""
    import re
    tokens = re.findall(r"[A-Z][a-z]+(?:\s[A-Z][a-z]+)*", raw)
    return tokens[0] if tokens else None


def classify(raw: str) -> ClassifiedTransaction:
    lowered = raw.lower()

    for keywords, category in _RULES:
        for kw in keywords:
            if kw in lowered:
                return ClassifiedTransaction(
                    raw=raw,
                    category=category,
                    merchant=_extract_merchant(raw),
                    amount=_extract_amount(raw),
                    confidence=0.85,
                )

    return ClassifiedTransaction(
        raw=raw,
        category=TransactionCategory.UNKNOWN,
        merchant=_extract_merchant(raw),
        amount=_extract_amount(raw),
        confidence=0.40,
    )


def classify_many(raws: list[str]) -> list[ClassifiedTransaction]:
    return [classify(r) for r in raws]
