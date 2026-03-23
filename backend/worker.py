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

async def shutdown(ctx):
    logging.info("Worker shutting down...")

class WorkerSettings:
    functions = [process_deck_upload_task]
    redis_settings = RedisSettings(host=config.REDIS_HOST, port=config.REDIS_PORT)
    queue_name = f"{config.REDIS_KEY_PREFIX}default"  # Prefixed queue to avoid collisions
    on_startup = startup
    on_shutdown = shutdown
