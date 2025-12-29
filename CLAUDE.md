# Demo Gauntlet

Demo Gauntlet MVP - document processing and challenge evaluation platform.

---

## Environment Setup

```bash
# Activate virtual environment (REQUIRED before any Python commands)
source .venv/bin/activate

# Install dependencies (if needed)
pip install -e .

# Install dev dependencies
pip install -e ".[dev]"
```

---

## Local Access

| Service | Domain | Port |
|---------|--------|------|
| Frontend (Vite) | http://demo-gauntlet.test | 3103 |
| Backend API | http://demo-gauntlet-api.test | 5003 |

Port assignments are defined in `~/Development/dev/ports.json` (authoritative).

---

## Commands

```bash
# Start backend API
uvicorn backend.main:app --host 127.0.0.1 --reload --port 5003

# Start frontend (from frontend/ directory)
cd frontend && npm run dev -- --port 3103 --strictPort

# Run tests
pytest

# Type checking
mypy backend/

# Linting
pylint backend/
```

---

## Project Structure

```
backend/
  main.py              # FastAPI entrypoint
  api/                 # API routes
  challenges/          # Challenge logic
  evaluation/          # Evaluation engine
  ingestion/           # Document ingestion
  models/              # Data models
  services/            # Business logic
  session/             # Session management
  migrations/          # Alembic migrations
frontend/              # Vite frontend
data/                  # Data files
deployment/            # Deployment configs
```

---

## Notes

- Package name: `demo-gauntlet`
- Requires Python >= 3.9
- Uses sentence-transformers + ChromaDB for embeddings
- PostgreSQL via SQLModel + Alembic
- Redis + ARQ for background jobs
- S3 (boto3) for file storage

---

## Isolation Settings

This project is configured to run alongside other local dev projects without conflicts.

| Resource | Setting | Notes |
|----------|---------|-------|
| Docker Redis port | 6381 | Host port mapped to container 6379 |
| API port | 5003 | Unique per `ports.json` |
| Frontend port | 3103 | Unique per `ports.json` |

### Docker Commands

```bash
# Start all services
docker compose up -d

# Start only Redis
docker compose up -d redis

# View logs
docker compose logs -f backend
```
