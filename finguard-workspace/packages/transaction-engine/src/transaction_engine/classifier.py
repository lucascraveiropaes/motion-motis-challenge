def classify_transaction(description: str) -> str:
    normalized = description.upper()

    if "STARBUCKS" in normalized or "MCDONALDS" in normalized:
        return "Food"
    if "NETFLIX" in normalized or "SPOTIFY" in normalized:
        return "Subscription"
    if "AMAZON" in normalized or "WALMART" in normalized:
        return "Shopping"

    return "Uncategorized"
