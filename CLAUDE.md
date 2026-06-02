# Demo Gauntlet

AI demo-practice simulator. FastAPI + Python backend, React/Vite/Tailwind frontend.
Upload a sales deck → research the prospect → face AI "challenger" personas.

---

## Architecture

The backend runs as **two separate services** in production (one container locally):

- **Web** — FastAPI (`backend.main:app`). Handles uploads, enqueues processing,
  serves results. Stateless; scales to zero.
- **Worker** — arq job (`backend.worker.WorkerSettings`) running one task,
  `process_deck_upload_task` (parse → OCR → embed → tag). Runs in `--burst`
  mode: drains the queue, then exits.

Because web and worker are separate containers, **no state is shared on local
disk** — everything goes through networked, scale-to-zero backends:

| Concern  | Backend                    | Config              |
|----------|----------------------------|---------------------|
| Job queue| Upstash Redis (serverless, TLS) | `REDIS_*`       |
| Files    | Google Cloud Storage       | `BLOB_STORAGE_TYPE=gcs`, `GCS_BUCKET_NAME` |
| Sessions | Neon Postgres (serverless) | `DATABASE_URL`      |

On upload, the web enqueues the job then triggers the worker Job
(`backend/services/worker_trigger.py`, best-effort). A Cloud Scheduler job runs
the worker every 2h as a safety-net drainer.

> Why this shape: the old single container (embedded Redis + in-process worker,
> `min-instances=1`) billed 24/7 and threw 5xx from CPU starvation between
> requests. The split makes everything pay-per-use.

---

## Environment Setup

```bash
source .venv/bin/activate          # REQUIRED
pip install -e .
pip install -e ".[dev]"            # test deps
```

### Local dev (single machine)

`docker-compose up` runs web + frontend + **local** Redis + worker together.
Locally `BLOB_STORAGE_TYPE=local` (disk) and `DATABASE_URL=sqlite` — the shared
backends above are production-only. Secrets live in `.env` (gitignored).

---

## Commands

```bash
uvicorn backend.main:app --host 127.0.0.1 --reload --port 8001   # API
npm --prefix frontend run dev                                    # frontend
pytest                                                           # tests
mypy .                                                           # type check
```

---

## Deployment (GCP project `substack-digest-05449`, region `us-central1`)

Build once, deploy to both targets:

```bash
IMG=us-central1-docker.pkg.dev/substack-digest-05449/cloud-run-source-deploy/demo-gauntlet:TAG
gcloud builds submit --tag "$IMG"                       # root Dockerfile (.dockerignore excludes .env*)

# Web service (min-instances=0)
gcloud run deploy demo-gauntlet-backend --image "$IMG" --region=us-central1 --min-instances=0 ...

# Worker Job (arq burst)
gcloud run jobs deploy demo-gauntlet-worker --image "$IMG" --region=us-central1 \
  --command=arq --args=backend.worker.WorkerSettings,--burst ...
```

- **Web**: Cloud Run service `demo-gauntlet-backend` (min=0).
- **Worker**: Cloud Run Job `demo-gauntlet-worker` (`arq … --burst`); web SA has
  `run.invoker` on it. Each run cold-starts + loads the embedding model
  (~60–90s), so end-to-end processing is ~2 min.
- **Frontend**: Vercel project `demo-gauntlet-ui` → auto-deploys on push to
  `main` (remote `portfolio` = `github.com/rjspence3/demo-gauntlet`; `origin` is
  dead).
- **Secrets** (Secret Manager, injected as env, never in the image):
  `upstash-redis-password`, `database-url`, `anthropic-api-key`,
  `openai-api-key`, `brave-api-key`, `demo-gauntlet-secret-key`.

---

## Testing

- **No API keys required.** `backend/tests/conftest.py` overrides the LLM
  dependencies (`get_agent`, `get_llm`) with `MockLLM`/`MockSearchClient` via
  `app.dependency_overrides` — the only mechanism FastAPI honors (`patch()`-ing
  the module attribute is silently ignored). Without this, keyless runs 500.
- In-memory test SQLite uses **`StaticPool`** so all threads share one DB.
- The slowapi limiter is **reset between tests** (all tests share the
  `testclient` IP, so counts would otherwise bleed).
- CI: `.github/workflows/ci.yml` runs `pytest backend/tests/` against a Redis
  service container with `DATABASE_URL=sqlite:///:memory:` and no API keys.

---

## Gotchas

- `SessionStore.engine` is a **lazy property** (resolves `backend.database.engine`
  at call time). Don't capture the engine in `__init__` — the singleton is built
  at import, before tests can patch it.
- The deployed image is built from the **root `Dockerfile`** (`COPY . .`);
  `.dockerignore` must keep excluding `.env*` or secrets leak into the image.
- Worker connects to Upstash over TLS; `RedisSettings` sets `conn_timeout=15` +
  retries (arq's 1s default crashes the burst worker under load).

---

## Structure

```
backend/   api/ challenges/ evaluation/ ingestion/ migrations/ models/
           research/ services/ session/ tests/ worker.py main.py
frontend/  src/{api,components,components/ui,lib}
docs/plan/ design-time planning docs (historical)
deployment/ legacy k8s/Cloud Run manifests (not the source of truth)
```
