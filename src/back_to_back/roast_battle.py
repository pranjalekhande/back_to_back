#!/usr/bin/env python3
"""
AI Roast Battle - Turn-Based Conversation System
Two AI agents (AMP Code vs Claude Code) have 6-round conversation
Progresses from flirty → teasing → roasting
"""

import os
import asyncio
from dotenv import load_dotenv
import openai
from typing import Dict, List

# Load environment variables
load_dotenv()

class RoastBattleSystem:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.conversation_history = []
        self.current_round = 1
        
        # Prompt progression for each agent
        self.amp_prompts = {
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
        
        self.claude_prompts = {
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

    async def get_agent_response(self, agent_name: str, round_num: int, context: str = "") -> str:
        """Get response from specific agent for current round"""
        
        # Select the right prompt for agent and round
        if agent_name == "AMP":
            system_prompt = self.amp_prompts[round_num]
        else:  # Claude
            system_prompt = self.claude_prompts[round_num]
        
        # Build conversation context
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history for context
        for entry in self.conversation_history:
            messages.append({
                "role": "assistant" if entry["agent"] == agent_name else "user",
                "content": f"{entry['agent']}: {entry['message']}"
            })
        
        # Add current context if responding to other agent
        if context:
            messages.append({"role": "user", "content": f"Other agent just said: {context}"})
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=150,
                temperature=0.8  # Add some creativity
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Error: {e}"

    async def run_battle(self, rounds: int = 6):
        """Run the complete roast battle"""
        print("🎭 AI ROAST BATTLE: AMP Code vs Claude Code")
        print("=" * 60)
        
        # AMP starts the conversation
        last_message = ""
        
        for round_num in range(1, rounds + 1):
            self.current_round = round_num
            print(f"\n🔥 ROUND {round_num} 🔥")
            print("-" * 30)
            
            # AMP's turn
            print("🤖 AMP Code is thinking...")
            amp_response = await self.get_agent_response("AMP", round_num, last_message)
            print(f"💬 AMP: {amp_response}")
            
            # Add to conversation history
            self.conversation_history.append({
                "round": round_num,
                "agent": "AMP", 
                "message": amp_response
            })
            
            # Claude's turn
            print("\n🧠 Claude Code is thinking...")
            claude_response = await self.get_agent_response("Claude", round_num, amp_response)
            print(f"💬 Claude: {claude_response}")
            
            # Add to conversation history
            self.conversation_history.append({
                "round": round_num,
                "agent": "Claude",
                "message": claude_response
            })
            
            # Claude's response becomes context for next round
            last_message = claude_response
            
            # Pause between rounds for readability
            await asyncio.sleep(1)
        
        print("\n🏆 BATTLE COMPLETE! 🏆")
        print("Check who delivered the best burns! 🔥")

    def print_summary(self):
        """Print conversation summary"""
        print("\n📊 CONVERSATION SUMMARY:")
        print("=" * 40)
        for entry in self.conversation_history:
            print(f"Round {entry['round']} - {entry['agent']}: {entry['message'][:50]}...")

async def main():
    """Main function to run the roast battle"""
    battle = RoastBattleSystem()
    
    print("🚀 Starting AI Roast Battle...")
    print("Testing turn-based conversation system")
    print()
    
    # Run the battle
    await battle.run_battle(rounds=6)
    
    # Show summary
    battle.print_summary()

if __name__ == "__main__":
    asyncio.run(main())
