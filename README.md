# fastapi-async

Finance Tracker API built with FastAPI + SQLAlchemy (SQLite) with a small static UI.

## Features

- User registration and simple auth via `Authorization: Bearer <login>`
- Wallets: create wallet, list wallets, total balance (with currency conversion to RUB)
- Operations: income, expense, transfer between wallets
- Static UI served from `/static`

## Tech stack

- FastAPI
- SQLAlchemy 2.x
- Pydantic 2.x
- SQLite

## Project structure

- `main.py` — FastAPI app, routers, static mount
- `app/api/v1/` — API routes
- `app/service/` — business logic
- `app/repository/` — DB access helpers
- `app/models.py` — SQLAlchemy models
- `app/schemas.py` — Pydantic schemas
- `app/static/` — HTML/CSS/JS UI
- `tests/` — API tests

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn main:app --reload
```

Open:

- API docs: `http://127.0.0.1:8000/docs`
- UI: `http://127.0.0.1:8000/static/index.html`

## Run tests

```bash
pytest -q
```

