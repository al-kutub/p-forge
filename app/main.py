"""FastAPI Quote API.

Endpoints:
    GET    /health          -> service health
    GET    /quotes          -> list all quotes
    GET    /quotes/random   -> a random quote
    GET    /quotes/{id}     -> a single quote
    POST   /quotes          -> create a quote (validated)
    DELETE /quotes/{id}     -> delete a quote
"""
from __future__ import annotations

from fastapi import FastAPI, HTTPException, Response, status

from .models import Quote, QuoteIn
from .store import QuoteStore


def create_app(store: QuoteStore | None = None) -> FastAPI:
    """Application factory so tests can inject a fresh, isolated store."""
    store = store if store is not None else QuoteStore()
    app = FastAPI(title="Quote API", version="1.0.0")

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok", "count": len(store.list())}

    @app.get("/quotes", response_model=list[Quote])
    def list_quotes() -> list[Quote]:
        return store.list()

    @app.get("/quotes/random", response_model=Quote)
    def random_quote() -> Quote:
        quote = store.random()
        if quote is None:
            raise HTTPException(status_code=404, detail="No quotes available")
        return quote

    @app.get("/quotes/{quote_id}", response_model=Quote)
    def get_quote(quote_id: int) -> Quote:
        quote = store.get(quote_id)
        if quote is None:
            raise HTTPException(status_code=404, detail="Quote not found")
        return quote

    @app.post("/quotes", response_model=Quote, status_code=status.HTTP_201_CREATED)
    def create_quote(payload: QuoteIn, response: Response) -> Quote:
        quote = store.add(payload)
        response.headers["Location"] = f"/quotes/{quote.id}"
        return quote

    @app.delete("/quotes/{quote_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_quote(quote_id: int) -> Response:
        if not store.delete(quote_id):
            raise HTTPException(status_code=404, detail="Quote not found")
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return app


app = create_app()
