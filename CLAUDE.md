# Demo Gauntlet

FastAPI + Python project.

---

## Environment Setup

```bash
# Activate virtual environment (REQUIRED)
source .venv/bin/activate

# Install dependencies
pip install -e .
pip install -e ".[dev]"  # includes test dependencies
```

---

## Commands

```bash
# Start API
uvicorn backend.main:app --host 127.0.0.1 --reload --port 8001

# Start frontend
npm run dev

# Run tests
pytest

# Type checking
mypy .
```

---

## Structure

```
backend/
  api/
    routers/
  challenges/
  dspy_optimization/
  evaluation/
  ingestion/
  migrations/
    versions/
  models/
  research/
  services/
  session/
  tests/
data/
  avatars/
  chroma_db/
  chroma_db_backup/
    9e05be18-0cf2-41e0-8c03-9b53ca1ce7c9/
    cd53b6d2-c123-44ef-ac77-f3ab50b97ed3/
  sessions/
    2a2f0c4f-6d65-42be-b9ab-3214852dda6c/
    4c08c7f4-b8f4-4807-ba23-bf5da3d03f7e/
    54ede032-1f13-4c29-9cde-74c91390b231/
    5abc8fc7-0b8d-42f0-a5ef-81855df66a14/
    6e1087a1-9116-4e19-b124-70feeafb11e1/
    70ae0a2e-96b4-4fa0-9223-33122752a800/
    8703b17c-950e-4cdd-af11-bbb9a26b0f2b/
    894badfd-369a-4f8f-89ca-310c941a9a56/
    b025e650-7794-4fe1-ae36-6b07dae5264f/
    s1/
    test-session/
demo_gauntlet.egg-info/
deployment/
dev/
doc/
docs/
  plan/
frontend/
  public/
    assets/
  src/
    api/
    assets/
    components/
    lib/
scripts/
```

---

## Notes

- Tech: FastAPI, Python
