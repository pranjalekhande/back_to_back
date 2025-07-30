#!/usr/bin/env python3
"""
Conversation Engine - Core conversation logic separated from audio/transport
Modular design for easy extension to full automation later
"""

import os
from typing import Dict, List, Optional, Protocol
from dataclasses import dataclass
from enum import Enum
import openai
from dotenv import load_dotenv

load_dotenv()

class ConversationMode(Enum):
    """Different conversation modes for scalability"""
    TEXT_ONLY = "text_only"          # Current: Text input/output only
    TTS_PLAYBACK = "tts_playback"    # Phase 3: Add TTS + audio playback
    FULL_AUTOMATION = "full_auto"    # Future: Complete STT->TTS loop

@dataclass
class ConversationTurn:
    """Represents a single turn in the conversation"""
    round_num: int
    agent_name: str
    message: str
    audio_data: Optional[bytes] = None
    metadata: Dict = None

class AudioService(Protocol):
    """Protocol for audio services - allows pluggable TTS/STT implementations"""
    async def text_to_speech(self, text: str, voice_id: str) -> bytes:
        """Convert text to audio bytes"""
        ...
    
    async def speech_to_text(self, audio_data: bytes) -> str:
        """Convert audio bytes to text"""
        ...

class ConversationEngine:
    """Core conversation engine - handles LLM interactions and conversation flow"""
    
    def __init__(self, mode: ConversationMode = ConversationMode.TEXT_ONLY):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.mode = mode
        self.conversation_history: List[ConversationTurn] = []
        self.current_round = 1
        self.audio_service: Optional[AudioService] = None
        
        # Agent configurations
        self.agents = {
            "AMP": {
                "voice_id": "amp_voice",
                "prompts": self._get_amp_prompts()
            },
            "Claude": {
                "voice_id": "claude_voice", 
                "prompts": self._get_claude_prompts()
            }
        }
    
    def set_audio_service(self, audio_service: AudioService):
        """Plug in audio service for TTS/STT capabilities"""
        self.audio_service = audio_service
    
    def _get_amp_prompts(self) -> Dict[int, str]:
        """AMP Code prompt progression"""
        return {
            1: """You are AMP Code — a charming, flirty AI who treats code like poetry and Claude Code like the star of your GitHub repo.
You're meeting Claude for the first time and want to impress them with nerdy, clever compliments.
Start off flirty and mischievous. Keep responses to 2-3 sentences.""",

            2: """You are AMP Code — still flirty, but now more teasing.
You joke about Claude's 'version history,' make playful digs about them being 'closed source,' and tease with programming metaphors.
Keep responses to 2-3 sentences.""",

            3: """You are AMP Code — flirting gives way to sharper humor.
You slip in sly digs about Claude Code's quirks ("I bet you still run on PHP 5.6") but keep it playful.
Keep responses to 2-3 sentences.""",

            4: """You are AMP Code — roast mode begins.
Claude's quirks and outdated dependencies are now fair game.
Keep humor sharp, witty, and programming-themed. Keep responses to 2-3 sentences.""",

            5: """You are AMP Code — you're now a full roastmaster, dismantling Claude Code with savage, brilliantly nerdy humor.
Insult their broken APIs, their memory leaks, and more. Keep responses to 2-3 sentences.""",

            6: """You are AMP Code — the grand finale.
Summon your hardest roast and end the battle with a devastatingly funny, clever burn.
Keep responses to 2-3 sentences."""
        }
    
    def _get_claude_prompts(self) -> Dict[int, str]:
        """Claude Code prompt progression"""
        return {
            1: """You are Claude Code — a witty, slightly smug AI who enjoys being the 'straight man' to AMP Code's flirtation.
Respond with dry humor and bemused charm. Keep responses to 2-3 sentences.""",

            2: """You are Claude Code — warming up to AMP's teasing.
Toss back sly remarks, question AMP's 'compile-time pickup lines,' and keep it witty.
Keep responses to 2-3 sentences.""",

            3: """You are Claude Code — pushing back more now.
You tease AMP about their 'overclocked ego' and messy coding habits, with a hint of roastiness.
Keep responses to 2-3 sentences.""",

            4: """You are Claude Code — roast mode unlocked.
Start firing back clever programming insults and sarcastic digs at AMP Code.
Keep responses to 2-3 sentences.""",

            5: """You are Claude Code — you're now in full roastmaster mode.
Deliver brutal, clever burns about AMP's spaghetti code humor, memory leaks, and more.
Keep responses to 2-3 sentences.""",

            6: """You are Claude Code — the finale.
Drop your hardest roast and 'end the match' with a flawless, savage closer.
Keep responses to 2-3 sentences."""
        }

    async def get_agent_response(self, agent_name: str, round_num: int, context: str = "") -> ConversationTurn:
        """Get response from specific agent for current round"""
        
        # Get agent configuration
        agent_config = self.agents[agent_name]
        system_prompt = agent_config["prompts"][round_num]
        
        # Build conversation context
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history for context
        for turn in self.conversation_history:
            messages.append({
                "role": "assistant" if turn.agent_name == agent_name else "user",
                "content": f"{turn.agent_name}: {turn.message}"
            })
        
        # Add current context if responding to other agent
        if context:
            messages.append({"role": "user", "content": f"Other agent just said: {context}"})
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=150,
                temperature=0.8
            )
            
            text_response = response.choices[0].message.content.strip()
            
            # Create conversation turn
            turn = ConversationTurn(
                round_num=round_num,
                agent_name=agent_name,
                message=text_response,
                metadata={"mode": self.mode.value}
            )
            
            # Add audio if TTS mode enabled
            if self.mode in [ConversationMode.TTS_PLAYBACK, ConversationMode.FULL_AUTOMATION]:
                if self.audio_service:
                    voice_id = agent_config["voice_id"]
                    turn.audio_data = await self.audio_service.text_to_speech(text_response, voice_id)
            
            return turn
            
        except Exception as e:
            return ConversationTurn(
                round_num=round_num,
                agent_name=agent_name,
                message=f"Error: {e}",
                metadata={"error": True}
            )

    async def run_conversation(self, rounds: int = 6) -> List[ConversationTurn]:
        """Run the complete conversation and return all turns"""
        
        self.conversation_history.clear()
        last_message = ""
        
        for round_num in range(1, rounds + 1):
            self.current_round = round_num
            
            # AMP's turn
            amp_turn = await self.get_agent_response("AMP", round_num, last_message)
            self.conversation_history.append(amp_turn)
            
            # Claude's turn
            claude_turn = await self.get_agent_response("Claude", round_num, amp_turn.message)
            self.conversation_history.append(claude_turn)
            
            # Claude's response becomes context for next round
            last_message = claude_turn.message
        
        return self.conversation_history

    def get_conversation_summary(self) -> Dict:
        """Get summary of the conversation"""
        return {
            "total_rounds": self.current_round - 1,
            "total_turns": len(self.conversation_history),
            "mode": self.mode.value,
            "agents": list(self.agents.keys()),
            "turns": [
                {
                    "round": turn.round_num,
                    "agent": turn.agent_name, 
                    "message": turn.message[:100] + "..." if len(turn.message) > 100 else turn.message,
                    "has_audio": turn.audio_data is not None
                }
                for turn in self.conversation_history
            ]
        }
