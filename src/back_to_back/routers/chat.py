"""Chat endpoints for AI conversation system."""

import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from redis.asyncio import Redis

from ..dependencies import get_redis
from ..models import (
    ChatRequest,
    ChatResponse,
    ConversationMode,
    ConversationPhase,
    ErrorResponse,
    InitRequest,
    InitResponse,
    SessionState,
    SpeakerType,
)
from ..services.conversation import ConversationService
from ..services.session import SessionService

router = APIRouter(tags=["chat"])


@router.post("/init", response_model=InitResponse)
async def initialize_session(
    request: InitRequest,
    redis: Redis = Depends(get_redis),
) -> InitResponse:
    """Initialize a new conversation session."""
    session_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()
    
    session_state = SessionState(
        session_id=session_id,
        agent_1_persona=request.agent_1_persona,
        agent_2_persona=request.agent_2_persona,
        mode=request.mode,
        scenario=request.scenario,
        max_turns=request.max_turns,
        created_at=timestamp,
        updated_at=timestamp,
    )
    
    session_service = SessionService(redis)
    await session_service.save_session(session_state)
    
    config = {
        "mode": request.mode.value,
        "max_turns": str(request.max_turns),
        "agent_1_persona": request.agent_1_persona[:100] + "..." if len(request.agent_1_persona) > 100 else request.agent_1_persona,
        "agent_2_persona": request.agent_2_persona[:100] + "..." if len(request.agent_2_persona) > 100 else request.agent_2_persona,
    }
    
    return InitResponse(session_id=session_id, config=config)


@router.post("/chat", response_model=ChatResponse)
async def process_chat_turn(
    request: ChatRequest,
    redis: Redis = Depends(get_redis),
) -> ChatResponse:
    """Process a chat turn."""
    session_service = SessionService(redis)
    session_state = await session_service.get_session(request.session_id)
    
    if not session_state:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session_state.current_turn >= session_state.max_turns:
        raise HTTPException(status_code=400, detail="Conversation has reached maximum turns")
    
    conversation_service = ConversationService()
    
    # Process the turn based on mode and current speaker
    if session_state.mode == ConversationMode.HUMAN_VS_AI:
        if session_state.next_speaker == SpeakerType.HUMAN and not request.message:
            raise HTTPException(status_code=400, detail="Human message required for human turn")
        
        response = await conversation_service.process_human_ai_turn(
            session_state, request.message, request.force_agent
        )
    else:
        response = await conversation_service.process_ai_ai_turn(
            session_state, request.force_agent
        )
    
    # Update session state
    session_state.current_turn += 1
    session_state.next_speaker = response.next_speaker
    session_state.conversation_phase = response.conversation_phase
    session_state.messages.append(response.message)
    session_state.updated_at = datetime.utcnow().isoformat()
    
    await session_service.save_session(session_state)
    
    return response


@router.get("/session/{session_id}")
async def get_session_info(
    session_id: str,
    redis: Redis = Depends(get_redis),
) -> dict:
    """Get session information and conversation history."""
    session_service = SessionService(redis)
    session_state = await session_service.get_session(session_id)
    
    if not session_state:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session_state.session_id,
        "mode": session_state.mode,
        "current_turn": session_state.current_turn,
        "max_turns": session_state.max_turns,
        "next_speaker": session_state.next_speaker,
        "conversation_phase": session_state.conversation_phase,
        "message_count": len(session_state.messages),
        "messages": session_state.messages,
        "created_at": session_state.created_at,
        "updated_at": session_state.updated_at,
    }


@router.delete("/session/{session_id}")
async def delete_session(
    session_id: str,
    redis: Redis = Depends(get_redis),
) -> dict[str, str]:
    """Delete a conversation session."""
    session_service = SessionService(redis)
    deleted = await session_service.delete_session(session_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"status": "deleted", "session_id": session_id}
