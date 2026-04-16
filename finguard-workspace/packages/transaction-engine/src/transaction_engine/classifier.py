import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# PoC rule-based fallback — used when OPENAI_API_KEY is not set
_CATEGORIES = {
    "Food": ["Starbucks", "McDonalds", "Subway"],
    "Subscription": ["Netflix", "Spotify", "Hulu"],
    "Shopping": ["Amazon", "Walmart", "Target"],
}

_SYSTEM_PROMPT = (
    "Classify the bank transaction description into exactly one of these categories: "
    "Food, Subscription, Shopping, Salary, Uncategorized. "
    "Return only the category name, nothing else."
)


def classify_transaction(description: str) -> str:
    """Classify a transaction description using LLM when available, rules otherwise."""
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        return _classify_with_llm(description, api_key)
    return _classify_with_rules(description)


def _classify_with_llm(description: str, api_key: str) -> str:
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": description},
        ],
        temperature=0,
    )
    return str(response.choices[0].message.content).strip()


def _classify_with_rules(description: str) -> str:
    """Hardcoded PoC — replaced by LLM in production."""
    lowered = description.lower()
    for category, keywords in _CATEGORIES.items():
        if any(keyword.lower() in lowered for keyword in keywords):
            return category
    return "Uncategorized"
