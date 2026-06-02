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


async def trigger_worker_job() -> None:
    """Execute the worker Cloud Run Job so it drains the queue and exits."""
    if not config.WORKER_JOB_NAME:
        return  # local dev / triggering disabled — long-lived worker handles the queue

    if not config.GCP_PROJECT:
        logger.warning("WORKER_JOB_NAME is set but GCP_PROJECT is missing; skipping worker trigger.")
        return

    try:
        from google.cloud import run_v2

        client = run_v2.JobsClient()
        name = client.job_path(config.GCP_PROJECT, config.GCP_REGION, config.WORKER_JOB_NAME)
        # run_job is a sync gRPC call returning a long-running op; fire-and-forget
        # off the event loop. We don't await completion — we only need it started.
        await asyncio.to_thread(client.run_job, name=name)
        logger.info("Triggered worker job '%s'.", config.WORKER_JOB_NAME)
    except Exception:
        logger.exception("Failed to trigger worker job; the Scheduler safety-net will drain the queue.")
