# Quote API

A small HTTP service for managing quotes, built with **FastAPI**. It supports
listing, fetching, random selection, creation, and deletion of quotes, ships
with seed data, validates input, and has a full test suite.

## Quick start

```bash
git clone https://github.com/al-kutub/p-forge.git
cd p-forge
./setup.sh
source .venv/bin/activate
uvicorn app.main:app --reload      # http://127.0.0.1:8000
```

Interactive API docs are available at `http://127.0.0.1:8000/docs` once running.

## Run the tests

```bash
source .venv/bin/activate
pytest
```

## Endpoints

| Method | Path             | Description                          |
|--------|------------------|--------------------------------------|
| GET    | `/health`        | Service health + quote count         |
| GET    | `/quotes`        | List all quotes                      |
| GET    | `/quotes/random` | Return a random quote                |
| GET    | `/quotes/{id}`   | Return a single quote by id          |
| POST   | `/quotes`        | Create a quote (returns 201)         |
| DELETE | `/quotes/{id}`   | Delete a quote (returns 204)         |

### Create payload

```json
{ "text": "Some wisdom here", "author": "Jane Doe" }
```

- `text` is required, 1–1000 characters.
- `author` is optional and defaults to `"Unknown"` (1–200 characters).

Invalid payloads return `422` with validation details. On success, `POST`
returns `201 Created` with a `Location` header pointing at the new resource.

## Examples

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/quotes
curl http://127.0.0.1:8000/quotes/random
curl http://127.0.0.1:8000/quotes/1
curl -X POST http://127.0.0.1:8000/quotes \
  -H 'Content-Type: application/json' \
  -d '{"text": "Talk is cheap.", "author": "Linus Torvalds"}'
curl -X DELETE http://127.0.0.1:8000/quotes/1
```

## Design

- **`app/models.py`** — Pydantic models (`QuoteIn`, `Quote`) defining the schema
  and validation rules.
- **`app/store.py`** — thread-safe in-memory `QuoteStore` with seed data. Each
  instance owns its id counter, keeping tests isolated.
- **`app/main.py`** — `create_app(store)` application factory wiring the routes;
  the factory lets tests inject a fresh store.
- **`tests/test_api.py`** — end-to-end tests via FastAPI's `TestClient`.

Storage is in-memory, so data resets on restart — appropriate for a demo /
reference service. Swapping in a persistent backend only requires implementing
the `QuoteStore` interface.
