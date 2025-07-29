"""WebSocket endpoints for real-time agent conversations using pipecat-flows architecture."""

import logging
from typing import Dict, Any
import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from ..services.agent_flow import AgentFlowService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["websocket"])

# Store active connections
active_connections: Dict[str, Dict[str, Any]] = {}


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    agent_1_persona: str = Query(..., description="Persona for agent 1"),
    agent_2_persona: str = Query(..., description="Persona for agent 2"),
    scenario: str = Query(default="flirt", description="Initial conversation scenario"),
    max_turns: int = Query(default=10, description="Maximum conversation turns")
):
    """WebSocket endpoint for real-time agent-to-agent conversations."""
    await websocket.accept()
    
    connection_id = f"session_{id(websocket)}"
    logger.info(f"WebSocket connection established: {connection_id}")
    
    try:
        # Initialize agent flow service
        flow_service = AgentFlowService()
        
        # Store connection info
        active_connections[connection_id] = {
            "websocket": websocket,
            "agent_1_persona": agent_1_persona,
            "agent_2_persona": agent_2_persona,
            "scenario": scenario,
            "max_turns": max_turns
        }
        
        # Start the agent conversation
        await flow_service.start_agent_conversation(
            agent_1_persona=agent_1_persona,
            agent_2_persona=agent_2_persona,
            scenario=scenario,
            max_turns=max_turns,
            websocket=websocket
        )
        
        # Send completion message
        await websocket.send_text("🎭 Conversation completed! Thanks for watching.")
        
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {connection_id}")
    except Exception as e:
        logger.error(f"Error in WebSocket connection {connection_id}: {e}")
        await websocket.close(code=1011, reason=str(e))
    finally:
        # Cleanup
        if connection_id in active_connections:
            del active_connections[connection_id]
        logger.info(f"Cleaned up connection: {connection_id}")


@router.get("/ws/stats")
async def get_websocket_stats() -> Dict[str, Any]:
    """Get statistics about active WebSocket connections."""
    return {
        "active_connections": len(active_connections),
        "connection_ids": list(active_connections.keys())
    }
