
category_clues = {
    "Food": ["Starbucks", "McDonalds", "Hotdog", "Burger"],
    "Subscription": ["Netflix", "Plus", "Spotify", "youtube"],
    "Shopping": ["Amazon", "Walmart", "Shopee"],
}

def classify_transaction(description: str) -> str:
    for category, clues in category_clues.items():
        for clue in clues:
            if clue in description:
                return category
    return "Uncategorized"