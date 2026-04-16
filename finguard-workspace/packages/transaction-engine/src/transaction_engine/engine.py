CATEGORIES = {
    "Food": ["Starbucks", "McDonalds", "Subway"],
    "Subscription": ["Netflix", "Spotify", "Hulu"],
    "Shopping": ["Amazon", "Walmart", "Target"],
}

def classify_transaction(description: str) -> str:
    description = description.lower()

    for category, keywords in CATEGORIES.items():
        if any(keyword.lower() in description for keyword in keywords):
            return category
        
    return "Uncategorized"