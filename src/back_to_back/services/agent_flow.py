"""Agent flow service using pipecat-ai for agent-to-agent conversations."""

import asyncio
import logging
from typing import Dict, Any, Optional

from pipecat.frames.frames import Frame, TextFrame, LLMMessagesFrame, TTSAudioRawFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineTask
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.processors.aggregators.sentence import SentenceAggregator
from pipecat.services.openai import OpenAILLMService, OpenAITTSService
from pipecat.transports.network.fastapi_websocket import FastAPIWebsocketTransport

logger = logging.getLogger(__name__)


class ConversationOrchestrator:
    """Orchestrates agent-to-agent conversations using pipecat-ai pipeline."""
    
    def __init__(
        self,
        agent_1_persona: str,
        agent_2_persona: str,
        openai_api_key: str,
        max_turns: int = 10
    ):
        self.agent_1_persona = agent_1_persona
        self.agent_2_persona = agent_2_persona
        self.openai_api_key = openai_api_key
        self.max_turns = max_turns
        self.current_turn = 0
        self.conversation_history = []
        self.scenario = "flirt"
        
        # Create LLM and TTS services for both agents
        self.agent_1_llm = OpenAILLMService(
            api_key=openai_api_key,
            model="gpt-4o-mini"
        )
        self.agent_2_llm = OpenAILLMService(
            api_key=openai_api_key, 
            model="gpt-4o-mini"
        )
        
        self.agent_1_tts = OpenAITTSService(
            api_key=openai_api_key,
            voice="alloy"
        )
        self.agent_2_tts = OpenAITTSService(
            api_key=openai_api_key,
            voice="nova"
        )
    
    def build_system_prompt(self, agent_name: str, persona: str, scenario: str) -> str:
        """Build the system prompt for an agent."""
        base_prompt = f"""You are {agent_name} with the following persona: {persona}

Current scenario: {scenario}

Instructions:
- Stay in character as described in your persona
- Keep responses conversational and engaging  
- Respond naturally to what the other agent says
- Don't break character or mention that you're an AI
- Keep responses under 100 words
- Be expressive and show personality
"""
        
        if scenario == "flirt":
            base_prompt += "\n- Be playful, charming, and flirtatious in your responses"
        elif scenario == "roast":
            base_prompt += "\n- Be witty, sarcastic, and playfully roast the other agent"
        elif scenario == "debate":
            base_prompt += "\n- Present arguments and counterarguments thoughtfully"
        
        return base_prompt
    
    def prepare_messages(self, agent_name: str, persona: str, scenario: str) -> list:
        """Prepare message context for an agent."""
        system_prompt = self.build_system_prompt(agent_name, persona, scenario)
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history (last 10 messages for context)
        for msg in self.conversation_history[-10:]:
            role = "assistant" if msg["speaker"] == agent_name else "user"
            messages.append({
                "role": role,
                "content": msg["content"]
            })
        
        return messages
    
    async def get_agent_response(self, agent_name: str, persona: str, llm_service: OpenAILLMService) -> str:
        """Get a response from an agent using pipecat LLM service."""
        try:
            messages = self.prepare_messages(agent_name, persona, self.scenario)
            
            # Create LLM context frame
            context = OpenAILLMContext(messages=messages)
            
            # Process through LLM service
            response_frame = await llm_service.process_frame(LLMMessagesFrame(context.messages))
            
            # Extract text from response
            if hasattr(response_frame, 'text'):
                return response_frame.text
            elif hasattr(response_frame, 'content'):
                return response_frame.content
            else:
                return str(response_frame)
                
        except Exception as e:
            logger.error(f"Error getting response from {agent_name}: {e}")
            return f"I'm having trouble thinking of something to say right now..."
    
    def get_initial_prompt(self, scenario: str) -> str:
        """Get the initial conversation starter."""
        starters = {
            "flirt": "Hey there! I couldn't help but notice you from across the room...",
            "roast": "Well, well, well... look what the cat dragged in!",
            "debate": "I've been thinking about this topic, and I have to say..."
        }
        return starters.get(scenario, "Hello! How are you doing today?")
    
    async def run_conversation(self, websocket, scenario: str = "flirt"):
        """Run the agent-to-agent conversation."""
        self.scenario = scenario
        
        # Send initial message
        await websocket.send_text(
            f"🎭 Starting {scenario} conversation between Agent Alpha and Agent Beta..."
        )
        
        # Agent Alpha starts with initial prompt
        initial_message = self.get_initial_prompt(scenario)
        self.conversation_history.append({
            "speaker": "Agent Alpha",
            "content": initial_message,
            "turn": self.current_turn
        })
        
        await websocket.send_text(f"**Agent Alpha:** {initial_message}")
        await asyncio.sleep(2)
        
        self.current_turn += 1
        
        # Conversation loop
        while self.current_turn < self.max_turns:
            # Determine which agent responds
            current_agent = "Agent Beta" if self.current_turn % 2 == 1 else "Agent Alpha"
            current_persona = self.agent_2_persona if current_agent == "Agent Beta" else self.agent_1_persona
            current_llm = self.agent_2_llm if current_agent == "Agent Beta" else self.agent_1_llm
            
            # Get response from current agent
            response = await self.get_agent_response(current_agent, current_persona, current_llm)
            
            # Add to history
            self.conversation_history.append({
                "speaker": current_agent,
                "content": response,
                "turn": self.current_turn
            })
            
            # Send to frontend
            await websocket.send_text(f"**{current_agent}:** {response}")
            
            # Check for phase transition
            if self.current_turn == self.max_turns // 2 and scenario == "flirt":
                self.scenario = "roast"
                await websocket.send_text(
                    "🔥 The conversation is heating up... time for some playful roasting!"
                )
            
            await asyncio.sleep(2)
            self.current_turn += 1
        
        # Send completion message
        await websocket.send_text("🎭 Conversation completed! Thanks for watching.")


class AgentFlowService:
    """Service for creating and managing agent conversation flows using pipecat-ai."""
    
    def __init__(self):
        from ..config import settings
        self.openai_api_key = settings.OPENAI_API_KEY
        
    async def start_agent_conversation(
        self,
        agent_1_persona: str,
        agent_2_persona: str,
        scenario: str,
        max_turns: int,
        websocket
    ) -> None:
        """Start an agent-to-agent conversation using pipecat-ai."""
        
        if not self.openai_api_key:
            await websocket.send_text("❌ OpenAI API key not configured")
            return
        
        # Create conversation orchestrator
        orchestrator = ConversationOrchestrator(
            agent_1_persona=agent_1_persona,
            agent_2_persona=agent_2_persona,
            openai_api_key=self.openai_api_key,
            max_turns=max_turns
        )
        
        # Run the conversation
        await orchestrator.run_conversation(websocket, scenario)
    
    async def create_pipecat_pipeline(
        self,
        agent_1_persona: str,
        agent_2_persona: str,
        scenario: str,
        max_turns: int,
        transport: FastAPIWebsocketTransport
    ) -> Pipeline:
        """Create a full pipecat pipeline for agent conversations (future enhancement)."""
        
        # This is where we would create a full pipecat pipeline
        # For now, we use the orchestrator approach above
        # Future: implement with pipecat frames and processors
        
        pipeline = Pipeline([
            SentenceAggregator(),
            # Agent processors would go here
            transport
        ])
        
        return pipeline
