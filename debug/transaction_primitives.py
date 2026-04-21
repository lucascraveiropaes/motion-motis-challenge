"""Core transaction classification primitives for the FinGuard exercise.

This module is intentionally small so candidates can reason about behavior from
source and docstrings without opening tests.
"""


class Transaction:
    """Simple transaction value object.

    Args:
        amount: Numeric transaction amount (same currency across comparisons).
        merchant: Merchant display name.
        channel: Origin channel, for example ``"web"`` or ``"mobile"``.
    """

    def __init__(self, amount, merchant, channel):
        self.amount = amount
        self.merchant = merchant
        self.channel = channel


class ClassificationService:
    """Classifies transaction channel and applies basic suspicious-amount rules.

    Behavior contract:
    - Classification is deterministic for the same transaction attributes.
    - Channel differences must be reflected in the returned class label.
    - Suspicious flagging uses a threshold of ``1000`` and is inclusive
      (amounts equal to ``1000`` are suspicious).
    """

    def __init__(self):
        """Initialize an in-memory cache used by :meth:`classify`.

        Cache entries should be keyed by all classification-relevant attributes
        so one transaction variant does not overwrite another.
        """
        self.cache = {}

    def classify(self, tx: Transaction):
        """Return the transaction class label.

        Expected labels:
        - ``"online_purchase"`` when ``tx.channel == "web"``
        - ``"mobile_purchase"`` for non-web channels (for this exercise)

        Notes:
        - Keep results stable for identical transaction inputs.
        - Ensure cache keys include channel information so transactions that
          share amount/merchant but differ by channel still classify differently.
        """
        key = (tx.merchant, tx.amount)

        if key in self.cache:
            return self.cache[key]

        if tx.channel == "web":
            result = "online_purchase"
        else:
            result = "mobile_purchase"

        self.cache[key] = result
        return result

    def is_suspicious(self, tx: Transaction):
        """Return whether a transaction is suspicious by amount.

        Rule:
        - Return ``True`` when ``tx.amount >= 1000``.
        - Return ``False`` otherwise.
        """
        threshold = 1000

        if tx.amount > threshold:
            return True
        return False
