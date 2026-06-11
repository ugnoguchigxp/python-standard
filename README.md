# FastAPI Standard Starter Template

A monolithic FastAPI + React starter template designed for high performance, ease of use, and multi-variant database configurations.

## Architecture

- **Backend**: FastAPI, SQLModel (Pydantic v2 + SQLAlchemy 2.0), Alembic, slowapi (rate limiter), secure (security headers), Uvicorn.
- **Frontend**: React v19, Vite, Tailwind CSS v4, TanStack Router (file-based routing), TanStack Query, shadcn/ui.
- **Package Managers**: `uv` for Python/Backend, `pnpm` for Node.js/Frontend.

## Directory Structure

```text
python-standard/
  backend/           # FastAPI application
    app/
      api/           # API routes & dependencies
      core/          # configurations, security & logging
      db/            # database session & tables init
      models/        # SQLModel table definitions
      schemas/       # Pydantic validation schemas
      main.py        # FastAPI entrypoint
    tests/           # pytest async endpoint tests
    pyproject.toml   # backend dependencies and configs
  frontend/          # React + Vite application
    src/
      components/ui/ # shadcn components
      lib/           # fetch wrappers & auth provider
      routes/        # TanStack Router page views
      App.tsx        # main app providers wrapper
      main.tsx       # DOM mount entrypoint
    package.json     # frontend packages and scripts
  docker-compose.yml # PostgreSQL container setup
  docs/              # Variant management guidelines
  README.md
```

## Quick Start

### 1. Start the Backend

Make sure you have `uv` installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`).

```bash
cd backend
uv sync --extra dev
uv run fastapi dev app/main.py --port 8000
```
- The local SQLite database will be initialized automatically on startup (`sqlite.db` in `backend/`).
- API documentation will be available at [http://localhost:8000/api/docs](http://localhost:8000/api/docs).

### 2. Start the Frontend

Make sure you have Node.js and `pnpm` installed.

```bash
cd frontend
pnpm install
pnpm dev
```
- The frontend will start at [http://localhost:5173](http://localhost:5173).
- API requests under `/api/*` are proxied to `http://localhost:8000` automatically.

## Running Tests & Verifications

### Backend
```bash
cd backend
# Run test suite
uv run pytest
# Lint checks
uv run ruff check .
# Format checks
uv run ruff format --check .
```

### Frontend
```bash
cd frontend
# Build checks
pnpm build
```

## Variant Management

This project uses Git branches to maintain variants (e.g., PostgreSQL driver settings, Cloudflare Workers configuration, api-only mode).
For instructions on applying overlays or switching variants, please read [docs/template-variant-management.md](docs/template-variant-management.md).
