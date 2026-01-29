"""
Health check endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from backend.database import get_session
from backend.config import config
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["health"])

@router.get("/health")
async def health_check(db: Session = Depends(get_session)) -> dict[str, str]:
    """
    Basic health check.
    """
    status = {"status": "ok"}
    
    # Check Database
    try:
        db.exec(select(1)).first()
        status["database"] = "ok"
    except Exception as e:
        logger.error(f"Health check failed for database: {e}")
        status["database"] = "error"
        status["status"] = "degraded"

    # Check Redis
    try:
        import redis
        r = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, socket_connect_timeout=1)
        r.ping()
        r.close()
        status["redis"] = "ok"
    except Exception as e:
        logger.error(f"Health check failed for redis: {e}")
        status["redis"] = "error"
        status["status"] = "degraded"
        
    return status
