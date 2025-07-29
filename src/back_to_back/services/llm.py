"""Large Language Model service."""

import os
from typing import Optional

import httpx
from openai import AsyncOpenAI

from ..models import ConversationPhase, SpeakerType


class LLMService:
    """Service for interacting with Language Models."""
    
    def __init__(self):
        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"  # Cost-effective model for conversations
    
    async def generate_response(
        self,
        persona: str,
        other_persona: str,
        conversation_history: str,
        phase: ConversationPhase,
        scenario: Optional[str] = None,
        speaker: SpeakerType = SpeakerType.AGENT_1,
    ) -> str:
        """Generate AI response based on context and persona."""
        
        # Build system prompt based on conversation phase
        system_prompt = self._build_system_prompt(
            persona, other_persona, phase, scenario, speaker
        )
        
        # Build user prompt with conversation context
        user_prompt = self._build_user_prompt(conversation_history, phase)
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=200,  # Keep responses concise for chat
                temperature=0.8,  # Add some creativity
                presence_penalty=0.1,  # Encourage diverse responses
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            # Fallback response in case of API failure
            return f"[AI Error: {str(e)}] Sorry, I'm having trouble responding right now."
    
    def _build_system_prompt(
        self,
        persona: str,
        other_persona: str,
        phase: ConversationPhase,
        scenario: Optional[str],
        speaker: SpeakerType,
    ) -> str:
        """Build system prompt based on persona and conversation phase."""
        
        base_prompt = f"""You are an AI agent in a conversation system. Your persona is: {persona}

You are talking to another agent with this persona: {other_persona}

"""
        
        if scenario:
            base_prompt += f"Scenario context: {scenario}\n\n"
        
        # Add phase-specific instructions
        phase_instructions = {
            ConversationPhase.INTRODUCTION: """This is the introduction phase. Be friendly, curious, and try to get to know the other agent. Ask questions about their interests, background, or opinions. Keep the tone light and engaging.""",
            
            ConversationPhase.CONVERSATION: """This is the main conversation phase. Engage in meaningful dialogue based on your persona. Share opinions, experiences, and react to what the other agent says. Be authentic to your character.""",
            
            ConversationPhase.FLIRT: """This is the flirting phase. Be playful, charming, and slightly flirtatious in your responses. Use humor, compliments, and subtle romantic undertones while staying respectful.""",
            
            ConversationPhase.ROAST: """This is the roasting phase. Be witty, sarcastic, and playfully mock the other agent. Use clever insults and humorous jabs, but keep it fun and not genuinely mean-spirited.""",
        }
        
        base_prompt += phase_instructions.get(phase, "Engage in natural conversation.")
        
        base_prompt += """

IMPORTANT GUIDELINES:
- Keep responses under 100 words
- Stay in character based on your persona
- Respond naturally to the conversation flow
- Don't mention that you're an AI or in a simulation
- Be engaging and entertaining
- Match the energy and tone of the conversation phase
"""
        
        return base_prompt
    
    def _build_user_prompt(self, conversation_history: str, phase: ConversationPhase) -> str:
        """Build user prompt with conversation context."""
        if not conversation_history:
            return f"Start the conversation in the {phase.value} phase. Make your first statement."
        
        return f"""Here's the conversation so far:

{conversation_history}

Respond as your character in the {phase.value} phase. Keep your response natural and engaging."""
