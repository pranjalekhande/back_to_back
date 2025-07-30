"""Session management service."""

import json
from typing import Optional

from redis.asyncio import Redis

from ..models import SessionState


class SessionService:
    """Service for managing conversation sessions in Redis."""
    
    def __init__(self, redis: Redis):
        self.redis = redis
        self.session_prefix = "session:"
        self.session_ttl = 3600 * 24  # 24 hours
    
    async def save_session(self, session_state: SessionState) -> None:
        """Save session state to Redis."""
        key = f"{self.session_prefix}{session_state.session_id}"
        data = session_state.model_dump_json()
        await self.redis.setex(key, self.session_ttl, data)
    
    async def get_session(self, session_id: str) -> Optional[SessionState]:
        """Get session state from Redis."""
        key = f"{self.session_prefix}{session_id}"
        data = await self.redis.get(key)
        
        if not data:
            return None
        
        return SessionState.model_validate_json(data)
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete session from Redis."""
        key = f"{self.session_prefix}{session_id}"
        result = await self.redis.delete(key)
        return result > 0
    
    async def extend_session_ttl(self, session_id: str) -> bool:
        """Extend session TTL."""
        key = f"{self.session_prefix}{session_id}"
        return await self.redis.expire(key, self.session_ttl)
