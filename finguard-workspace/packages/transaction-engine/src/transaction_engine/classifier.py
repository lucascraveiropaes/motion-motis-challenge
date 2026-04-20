def classify_transaction(description: str) -> str:
    """
    Classify a transaction description into a standard category.
    This is a basic rule-based implementation.
    """
    desc_lower = description.lower()

    if "starbucks" in desc_lower or "mcdonalds" in desc_lower:
        return "Food"
    if "netflix" in desc_lower or "spotify" in desc_lower:
        return "Subscription"
    if "amazon" in desc_lower or "walmart" in desc_lower:
        return "Shopping"

    return "Uncategorized"
