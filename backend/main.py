from fastapi import FastAPI

from backend.ingestion import router as ingestion_router
from backend.research import router as research_router
from backend.challenges import router as challenges_router

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Demo Gauntlet API")

from backend.config import config

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from backend.evaluation import router as evaluation_router

app.include_router(ingestion_router.router)
app.include_router(research_router.router)
app.include_router(challenges_router.router)
app.include_router(evaluation_router.router)

@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}
