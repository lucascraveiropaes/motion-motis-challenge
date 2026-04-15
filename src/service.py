import asyncio
import re
from datetime import datetime, timezone
from typing import AsyncGenerator

from src.models import Category, ClassificationResult


CLASSIFICATION_RULES: dict[Category, list[tuple[str, float]]] = {
    Category.FOOD: [
        (r"\bstarbucks\b", 0.95),
        (r"\bmcdonald's?\b", 0.95),
        (r"\bburger king\b", 0.90),
        (r"\bsubway\b", 0.90),
        (r"\bpizza hut\b", 0.90),
        (r"\bwendy's\b", 0.90),
        (r"\bchick-fil-a\b", 0.90),
    ],
    Category.ENTERTAINMENT: [
        (r"\bnetflix\b", 0.95),
        (r"\bspotify\b", 0.95),
        (r"\byoutube\b", 0.90),
        (r"\bdisney\+\b", 0.95),
        (r"\bhulu\b", 0.90),
        (r"\bamazon prime\b", 0.90),
        (r"\bhbomax\b", 0.85),
    ],
}


class Classifier:
    def classify(self, description: str) -> tuple[Category, float]:
        normalized = description.lower().strip()
        best_match = Category.OTHER
        best_confidence = 0.5

        for category, patterns in CLASSIFICATION_RULES.items():
            for pattern, confidence in patterns:
                if re.search(pattern, normalized, re.IGNORECASE):
                    if confidence > best_confidence:
                        best_match = category
                        best_confidence = confidence

        if best_confidence == 0.5:
            best_confidence = 0.3

        return best_match, best_confidence

    def classify_result(self, description: str) -> ClassificationResult:
        category, confidence = self.classify(description)
        return ClassificationResult(
            description=description,
            category=category,
            confidence=confidence,
        )

    async def classify_stream(
        self, descriptions: list[str], delay_ms: int = 100
    ) -> AsyncGenerator[ClassificationResult, None]:
        for description in descriptions:
            await asyncio.sleep(delay_ms / 1000)
            yield self.classify_result(description)

    def classify_batch(self, descriptions: list[str]) -> list[ClassificationResult]:
        return [self.classify_result(d) for d in descriptions]


classifier = Classifier()
