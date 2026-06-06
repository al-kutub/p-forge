"""End-to-end tests for the Quote API using FastAPI's TestClient."""
import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.store import QuoteStore


@pytest.fixture
def client():
    # Fresh, isolated store per test.
    return TestClient(create_app(QuoteStore()))


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["count"] == 8


def test_list_quotes(client):
    r = client.get("/quotes")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 8
    assert all({"id", "text", "author"} <= q.keys() for q in data)


def test_get_quote(client):
    r = client.get("/quotes/1")
    assert r.status_code == 200
    assert r.json()["id"] == 1


def test_get_quote_not_found(client):
    r = client.get("/quotes/9999")
    assert r.status_code == 404


def test_random_quote(client):
    r = client.get("/quotes/random")
    assert r.status_code == 200
    assert "text" in r.json()


def test_create_quote(client):
    r = client.post("/quotes", json={"text": "Hello world", "author": "Tester"})
    assert r.status_code == 201
    body = r.json()
    assert body["text"] == "Hello world"
    assert body["author"] == "Tester"
    assert r.headers["Location"] == f"/quotes/{body['id']}"
    # Newly created quote is retrievable.
    assert client.get(f"/quotes/{body['id']}").status_code == 200


def test_create_quote_default_author(client):
    r = client.post("/quotes", json={"text": "No author given"})
    assert r.status_code == 201
    assert r.json()["author"] == "Unknown"


def test_create_quote_empty_text_rejected(client):
    r = client.post("/quotes", json={"text": "", "author": "X"})
    assert r.status_code == 422


def test_create_quote_missing_text_rejected(client):
    r = client.post("/quotes", json={"author": "X"})
    assert r.status_code == 422


def test_delete_quote(client):
    r = client.delete("/quotes/1")
    assert r.status_code == 204
    assert client.get("/quotes/1").status_code == 404


def test_delete_quote_not_found(client):
    r = client.delete("/quotes/9999")
    assert r.status_code == 404
