"""
Main entry point for the FastAPI application.
"""
from fastapi import FastAPI

from backend.ingestion import router as ingestion_router
from backend.research import router as research_router
from backend.challenges import router as challenges_router
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

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    app.state.arq_pool = await create_pool(RedisSettings(host=config.REDIS_HOST, port=config.REDIS_PORT))
    app.state.arq_queue_name = f"{config.REDIS_KEY_PREFIX}default"  # Prefixed queue name
    yield
    await app.state.arq_pool.close()

app = FastAPI(title="Demo Gauntlet API", lifespan=lifespan)

from backend.config import config

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.allowed_origins_list,
    allow_credentials=True,
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
