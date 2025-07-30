"""FastAPI application for AI agent conversation system."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import redis.asyncio as redis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import audio, chat, health, websocket


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    # Initialize Redis connection
    app.state.redis = redis.from_url("redis://localhost:6379", decode_responses=True)
    
    yield
    
    # Cleanup
    await app.state.redis.close()


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="Back to Back AI Chat",
        description="AI agent conversation system with TTS",
        version="0.1.0",
        lifespan=lifespan,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(health.router, prefix="/api/v1")
    app.include_router(chat.router, prefix="/api/v1")  # Keep for backwards compatibility
    app.include_router(websocket.router)  # New pipecat-flows WebSocket endpoint
    app.include_router(audio.router)  # No prefix for audio serving

    return app


app = create_app()
