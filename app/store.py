"""In-memory quote store with seed data.

The store is intentionally simple and self-contained so the API runs with no
external database. Each store instance keeps its own id counter so tests are
isolated from one another.
"""
from __future__ import annotations

from threading import Lock

from .models import Quote, QuoteIn

SEED_QUOTES = [
    ("The only way to do great work is to love what you do.", "Steve Jobs"),
    ("Simplicity is the ultimate sophistication.", "Leonardo da Vinci"),
    ("Premature optimization is the root of all evil.", "Donald Knuth"),
    ("Talk is cheap. Show me the code.", "Linus Torvalds"),
    ("First, solve the problem. Then, write the code.", "John Johnson"),
    ("Programs must be written for people to read.", "Harold Abelson"),
    ("Make it work, make it right, make it fast.", "Kent Beck"),
    ("Stay hungry, stay foolish.", "Steve Jobs"),
]


class QuoteStore:
    """Thread-safe in-memory collection of quotes."""

    def __init__(self, seed: bool = True):
        self._quotes: dict[int, Quote] = {}
        self._next_id = 1
        self._lock = Lock()
        if seed:
            for text, author in SEED_QUOTES:
                self.add(QuoteIn(text=text, author=author))

    def add(self, payload: QuoteIn) -> Quote:
        with self._lock:
            quote = Quote(id=self._next_id, **payload.model_dump())
            self._quotes[quote.id] = quote
            self._next_id += 1
            return quote

    def list(self) -> list[Quote]:
        return list(self._quotes.values())

    def get(self, quote_id: int) -> Quote | None:
        return self._quotes.get(quote_id)

    def random(self) -> Quote | None:
        import random

        with self._lock:
            if not self._quotes:
                return None
            return random.choice(list(self._quotes.values()))

    def delete(self, quote_id: int) -> bool:
        with self._lock:
            return self._quotes.pop(quote_id, None) is not None
