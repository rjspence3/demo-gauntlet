"""
Main entry point for the FastAPI application.
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging

from backend.ingestion import router as ingestion_router
from backend.research import router as research_router
from backend.challenges import router as challenges_router
from backend.api.routers import challengers as challengers_management_router
from backend.api.routers import auth as auth_router

from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager
from backend.database import init_db
from arq import create_pool
from arq.connections import RedisSettings
from backend.config import config
from backend.limiter import limiter
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info("Starting up...")
        init_db()
        config.validate_security()
        from backend.ingestion.parser import validate_ocr_dependencies
        validate_ocr_dependencies()
        app.state.arq_pool = await create_pool(RedisSettings(host=config.REDIS_HOST, port=config.REDIS_PORT))
        app.state.arq_queue_name = f"{config.REDIS_KEY_PREFIX}default"  # Prefixed queue name
        yield
    except Exception as e:
        logger.critical(f"Startup failed: {e}")
        raise e
    finally:
        logger.info("Shutting down...")
        if hasattr(app.state, "arq_pool"):
            await app.state.arq_pool.close()

app = FastAPI(title="Demo Gauntlet API", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error. Please check server logs."},
    )

from backend.config import config

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.allowed_origins_list,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

from backend.evaluation import router as evaluation_router

from backend.api.routers import health as health_router

app.include_router(ingestion_router.router)
app.include_router(research_router.router)
app.include_router(challenges_router.router)
app.include_router(challengers_management_router.router)
app.include_router(evaluation_router.router)
app.include_router(auth_router.router)
app.include_router(health_router.router)
from backend.api.routers import live as live_router
app.include_router(live_router.router)
from backend.probes import router as probes_router
app.include_router(probes_router.router)
