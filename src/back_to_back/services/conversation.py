"""Conversation management service."""

from datetime import datetime
from typing import Optional

from ..models import (
    ChatMessage,
    ChatResponse,
    ConversationPhase,
    SessionState,
    SpeakerType,
)
from .llm import LLMService
from .tts import TTSService


class ConversationService:
    """Service for managing AI conversations."""
    
    def __init__(self):
        self.llm_service = LLMService()
        self.tts_service = TTSService()
    
    async def process_ai_ai_turn(
        self,
        session_state: SessionState,
        force_agent: Optional[SpeakerType] = None,
    ) -> ChatResponse:
        """Process a turn in AI vs AI mode."""
        # Determine which agent should speak
        current_speaker = force_agent or session_state.next_speaker
        next_speaker = self._get_next_speaker(current_speaker, session_state)
        
        # Generate AI response
        agent_text = await self._generate_agent_response(session_state, current_speaker)
        
        # Generate TTS audio
        audio_url = await self.tts_service.synthesize_speech(
            agent_text, current_speaker
        )
        
        # Create message
        message = ChatMessage(
            speaker=current_speaker,
            text=agent_text,
            audio_url=audio_url,
            turn_number=session_state.current_turn + 1,
            timestamp=datetime.utcnow().isoformat(),
        )
        
        # Determine conversation phase
        phase = self._determine_conversation_phase(session_state)
        
        return ChatResponse(
            message=message,
            next_speaker=next_speaker,
            conversation_phase=phase,
            turn_count=session_state.current_turn + 1,
            is_conversation_complete=session_state.current_turn + 1 >= session_state.max_turns,
        )
    
    async def process_human_ai_turn(
        self,
        session_state: SessionState,
        human_message: Optional[str] = None,
        force_agent: Optional[SpeakerType] = None,
    ) -> ChatResponse:
        """Process a turn in Human vs AI mode."""
        current_speaker = session_state.next_speaker
        
        if current_speaker == SpeakerType.HUMAN:
            if not human_message:
                raise ValueError("Human message is required for human turn")
            
            # Create human message
            message = ChatMessage(
                speaker=SpeakerType.HUMAN,
                text=human_message,
                audio_url=None,  # Humans don't get TTS by default
                turn_number=session_state.current_turn + 1,
                timestamp=datetime.utcnow().isoformat(),
            )
            
            next_speaker = SpeakerType.AGENT_1  # AI responds next
        else:
            # AI turn
            ai_speaker = force_agent or SpeakerType.AGENT_1
            agent_text = await self._generate_agent_response(session_state, ai_speaker)
            
            audio_url = await self.tts_service.synthesize_speech(
                agent_text, ai_speaker
            )
            
            message = ChatMessage(
                speaker=ai_speaker,
                text=agent_text,
                audio_url=audio_url,
                turn_number=session_state.current_turn + 1,
                timestamp=datetime.utcnow().isoformat(),
            )
            
            next_speaker = SpeakerType.HUMAN  # Human responds next
        
        phase = self._determine_conversation_phase(session_state)
        
        return ChatResponse(
            message=message,
            next_speaker=next_speaker,
            conversation_phase=phase,
            turn_count=session_state.current_turn + 1,
            is_conversation_complete=session_state.current_turn + 1 >= session_state.max_turns,
        )
    
    def _get_next_speaker(
        self, current_speaker: SpeakerType, session_state: SessionState
    ) -> SpeakerType:
        """Determine the next speaker in AI vs AI mode."""
        if current_speaker == SpeakerType.AGENT_1:
            return SpeakerType.AGENT_2
        else:
            return SpeakerType.AGENT_1
    
    def _determine_conversation_phase(self, session_state: SessionState) -> ConversationPhase:
        """Determine the current conversation phase based on turn count."""
        turn_ratio = session_state.current_turn / session_state.max_turns
        
        if turn_ratio < 0.3:
            return ConversationPhase.INTRODUCTION
        elif turn_ratio < 0.7:
            return ConversationPhase.CONVERSATION
        elif turn_ratio < 0.85:
            return ConversationPhase.FLIRT
        else:
            return ConversationPhase.ROAST
    
    async def _generate_agent_response(
        self, session_state: SessionState, speaker: SpeakerType
    ) -> str:
        """Generate AI response for the specified agent."""
        # Get persona for the speaking agent
        if speaker == SpeakerType.AGENT_1:
            persona = session_state.agent_1_persona
            other_persona = session_state.agent_2_persona
        else:
            persona = session_state.agent_2_persona
            other_persona = session_state.agent_1_persona
        
        # Build conversation context
        conversation_history = self._build_conversation_context(session_state)
        phase = self._determine_conversation_phase(session_state)
        
        # Generate response using LLM
        response = await self.llm_service.generate_response(
            persona=persona,
            other_persona=other_persona,
            conversation_history=conversation_history,
            phase=phase,
            scenario=session_state.scenario,
            speaker=speaker,
        )
        
        return response
    
    def _build_conversation_context(self, session_state: SessionState) -> str:
        """Build conversation context from message history."""
        if not session_state.messages:
            return ""
        
        context_lines = []
        for msg in session_state.messages[-10:]:  # Last 10 messages for context
            speaker_name = self._get_speaker_name(msg.speaker)
            context_lines.append(f"{speaker_name}: {msg.text}")
        
        return "\n".join(context_lines)
    
    def _get_speaker_name(self, speaker: SpeakerType) -> str:
        """Get display name for speaker."""
        if speaker == SpeakerType.AGENT_1:
            return "Agent 1"
        elif speaker == SpeakerType.AGENT_2:
            return "Agent 2"
        else:
            return "Human"
