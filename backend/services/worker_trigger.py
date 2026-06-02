"""
Triggers the demo-gauntlet worker Cloud Run Job to drain the arq queue.

Flow in production:
    upload  ->  enqueue_job (durable in Upstash Redis)  ->  trigger_worker_job()
The Job runs `arq backend.worker.WorkerSettings --burst`: it processes every
queued job, then exits. Nothing runs idle between uploads.

Locally (docker-compose) a long-lived worker is already running and
WORKER_JOB_NAME is unset, so triggering is a no-op.

Triggering is best-effort: the job is already durably queued before this runs,
so a failure to launch the worker must NOT fail the upload. A low-frequency
Cloud Scheduler run is the safety-net that drains anything a failed trigger left
behind.
"""
import asyncio
import logging

from backend.config import config

logger = logging.getLogger(__name__)

# Hold references to in-flight trigger tasks so the event loop doesn't garbage-
# collect them mid-execution (asyncio only keeps weak refs to bare tasks).
_pending: set = set()


async def trigger_worker_job() -> None:
    """
    Fire the worker Cloud Run Job to drain the queue. Truly fire-and-forget: the
    job is already durable in Redis, so the upload response must NOT block on the
    Cloud Run control plane (a gRPC hiccup would otherwise hang every upload).
    """
    if not config.WORKER_JOB_NAME:
        return  # local dev / triggering disabled — long-lived worker handles the queue

    if not config.GCP_PROJECT:
        logger.warning("WORKER_JOB_NAME is set but GCP_PROJECT is missing; skipping worker trigger.")
        return

    task = asyncio.create_task(_run_worker_job())
    _pending.add(task)
    task.add_done_callback(_pending.discard)


async def _run_worker_job() -> None:
    try:
        from google.cloud import run_v2

        client = run_v2.JobsClient()
        name = client.job_path(config.GCP_PROJECT, config.GCP_REGION, config.WORKER_JOB_NAME)
        await asyncio.to_thread(client.run_job, name=name)
        logger.info("Triggered worker job '%s'.", config.WORKER_JOB_NAME)
    except Exception:
        logger.exception("Failed to trigger worker job; the Scheduler safety-net will drain the queue.")
