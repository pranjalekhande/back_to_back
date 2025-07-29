"""Health check endpoints."""

from fastapi import APIRouter, Depends
from redis.asyncio import Redis

from ..dependencies import get_redis

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Basic health check endpoint."""
    return {"status": "healthy", "service": "back-to-back-api"}


@router.get("/health/redis")
async def redis_health_check(redis: Redis = Depends(get_redis)) -> dict[str, str]:
    """Check Redis connection health."""
    try:
        await redis.ping()
        return {"status": "healthy", "redis": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "redis": "disconnected", "error": str(e)}
