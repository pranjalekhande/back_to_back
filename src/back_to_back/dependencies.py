"""FastAPI dependencies."""

from fastapi import Request
from redis.asyncio import Redis


async def get_redis(request: Request) -> Redis:
    """Get Redis connection from app state."""
    return request.app.state.redis
