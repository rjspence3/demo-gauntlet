import logging
"""
Arq worker configuration for background tasks.
"""
import asyncio
from arq.connections import RedisSettings
from backend.config import config
from backend.ingestion.processor import process_deck_upload_task

async def startup(ctx):
    logging.info("Worker starting...")
    # Ensure tables exist — the worker may run before the web on a fresh DB.
    from backend.database import init_db
    init_db()

async def shutdown(ctx):
    logging.info("Worker shutting down...")

class WorkerSettings:
    functions = [process_deck_upload_task]
    redis_settings = RedisSettings(
        host=config.REDIS_HOST,
        port=config.REDIS_PORT,
        password=config.REDIS_PASSWORD,
        ssl=config.REDIS_SSL,
        # arq defaults conn_timeout to 1s — too tight for a TLS handshake to
        # managed Redis (Upstash) under load; transient latency would crash the
        # burst worker. Give it room + retries.
        conn_timeout=15,
        conn_retries=5,
        conn_retry_delay=1,
    )
    queue_name = f"{config.REDIS_KEY_PREFIX}default"  # Prefixed queue to avoid collisions
    on_startup = startup
    on_shutdown = shutdown
