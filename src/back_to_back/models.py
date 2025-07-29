"""Pydantic models for the AI chat application."""

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class SpeakerType(str, Enum):
    """Types of speakers in conversation."""
    AGENT_1 = "agent_1"
    AGENT_2 = "agent_2"
    HUMAN = "human"


class ConversationMode(str, Enum):
    """Conversation modes."""
    AI_VS_AI = "ai_vs_ai"
    HUMAN_VS_AI = "human_vs_ai"


class ConversationPhase(str, Enum):
    """Phases of conversation."""
    INTRODUCTION = "introduction"
    CONVERSATION = "conversation"
    ROAST = "roast"
    FLIRT = "flirt"


class InitRequest(BaseModel):
    """Request to initialize a new conversation session."""
    agent_1_persona: str = Field(..., description="Persona description for agent 1")
    agent_2_persona: str = Field(..., description="Persona description for agent 2")
    mode: ConversationMode = Field(default=ConversationMode.AI_VS_AI)
    scenario: Optional[str] = Field(None, description="Optional scenario description")
    max_turns: int = Field(default=20, ge=1, le=100)


class InitResponse(BaseModel):
    """Response after initializing a conversation."""
    session_id: str
    config: Dict[str, str]
    status: str = "initialized"


class ChatMessage(BaseModel):
    """A single chat message."""
    speaker: SpeakerType
    text: str
    audio_url: Optional[str] = None
    turn_number: int
    timestamp: str


class ChatRequest(BaseModel):
    """Request to process a chat turn."""
    session_id: str
    message: Optional[str] = Field(None, description="Human message (if human's turn)")
    force_agent: Optional[SpeakerType] = Field(None, description="Force specific agent to speak")


class ChatResponse(BaseModel):
    """Response from a chat turn."""
    message: ChatMessage
    next_speaker: SpeakerType
    conversation_phase: ConversationPhase
    turn_count: int
    is_conversation_complete: bool = False


class SessionState(BaseModel):
    """Internal session state stored in Redis."""
    session_id: str
    agent_1_persona: str
    agent_2_persona: str
    mode: ConversationMode
    scenario: Optional[str]
    max_turns: int
    current_turn: int = 0
    next_speaker: SpeakerType = SpeakerType.AGENT_1
    conversation_phase: ConversationPhase = ConversationPhase.INTRODUCTION
    messages: List[ChatMessage] = Field(default_factory=list)
    created_at: str
    updated_at: str


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    detail: Optional[str] = None
    session_id: Optional[str] = None
