"""Pydantic models for the Quote API."""
from pydantic import BaseModel, Field


class QuoteIn(BaseModel):
    """Payload for creating a quote."""

    text: str = Field(..., min_length=1, max_length=1000)
    author: str = Field(default="Unknown", min_length=1, max_length=200)


class Quote(QuoteIn):
    """A stored quote, with its server-assigned id."""

    id: int
