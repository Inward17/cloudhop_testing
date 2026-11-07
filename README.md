# cloudhop_testing

A small notes app for testing [Cloudhop](https://github.com/Inward17/CloudHop): deploys, cloud switches and monitoring.

- `api/`: Python FastAPI backend. Stores notes in Postgres when `DATABASE_URL` is set, otherwise in memory. `GET /` is the health check and shows where the app runs.
- `web/`: JavaScript frontend built with Vite. Lists, adds and deletes notes through the API.

What Cloudhop should find when it analyzes this repo: a FastAPI service in `api/` (port 8000, given the main address), a Vite static site in `web/` (served by nginx), and Postgres. It writes a Dockerfile for each and a Compose file with Postgres. Notes you add before a switch should still be there after it, because the database is copied.

## Run locally

API (port 8000), with notes in memory:

```bash
cd api && python -m venv .venv && .venv/bin/pip install -r requirements.txt && .venv/bin/uvicorn main:app --port 8000
```

Frontend (port 5173), in another terminal:

```bash
cd web && npm install && npm run dev
```

Open http://localhost:5173. Set `DATABASE_URL` (see `.env.example`) to use Postgres instead of memory.

## Test the API

```bash
cd api && .venv/bin/pip install pytest httpx && .venv/bin/python -m pytest
```

## How the frontend finds the API

Set `VITE_API_URL` when building to point at the API. Without it, the frontend uses the same host: port 8000 when running locally on 5173, and the main address (port 80) when Cloudhop runs both on one server.
