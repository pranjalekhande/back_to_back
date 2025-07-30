#!/usr/bin/env python3
"""
Modular AI Roast Battle System V2
Designed for scalability: TEXT_ONLY → TTS_PLAYBACK → FULL_AUTOMATION
"""

import asyncio
import os
import sys
sys.path.append(os.path.dirname(__file__))

from core.conversation_engine import ConversationEngine, ConversationMode
from audio.audio_services import AudioServiceFactory, AudioPlayer

class RoastBattleOrchestrator:
    """Orchestrates the roast battle with configurable modes"""
    
    def __init__(self, mode: ConversationMode = ConversationMode.TEXT_ONLY):
        self.mode = mode
        self.engine = ConversationEngine(mode)
        self.audio_player = AudioPlayer()
        
        # Configure audio service based on mode
        if mode in [ConversationMode.TTS_PLAYBACK, ConversationMode.FULL_AUTOMATION]:
            # Use real ElevenLabs TTS
            audio_service = AudioServiceFactory.create_service("elevenlabs")
            self.engine.set_audio_service(audio_service)
    
    async def run_battle(self, rounds: int = 6):
        """Run the roast battle with audio/visual presentation"""
        
        print("🎭 AI ROAST BATTLE: AMP Code vs Claude Code")
        print(f"Mode: {self.mode.value.upper()}")
        print("=" * 60)
        
        # Run the conversation
        conversation_turns = await self.engine.run_conversation(rounds)
        
        # Present the conversation based on mode
        await self._present_conversation(conversation_turns)
        
        # Show summary
        self._show_summary()
    
    async def _present_conversation(self, turns):
        """Present conversation based on current mode"""
        
        current_round = 0
        
        for turn in turns:
            # New round header
            if turn.round_num != current_round:
                current_round = turn.round_num
                print(f"\n🔥 ROUND {current_round} 🔥")
                print("-" * 30)
            
            # Show agent thinking
            agent_emoji = "🤖" if turn.agent_name == "AMP" else "🧠"
            print(f"{agent_emoji} {turn.agent_name} is thinking...")
            
            # Simulate thinking time
            await asyncio.sleep(0.5)
            
            # Show text response
            print(f"💬 {turn.agent_name}: {turn.message}")
            
            # Handle audio based on mode
            if self.mode == ConversationMode.TTS_PLAYBACK and turn.audio_data:
                print(f"🔊 Playing {turn.agent_name}'s voice...")
                await self.audio_player.play_audio(turn.audio_data, turn.agent_name)
            elif self.mode == ConversationMode.FULL_AUTOMATION and turn.audio_data:
                # In full automation, audio becomes input for next agent
                print(f"🔄 Audio → STT → Next Agent...")
                # Future: Process audio through STT pipeline
            
            # Pause between turns for readability
            await asyncio.sleep(1)
    
    def _show_summary(self):
        """Show battle summary"""
        summary = self.engine.get_conversation_summary()
        
        print("\n🏆 BATTLE COMPLETE! 🏆")
        print("=" * 40)
        print(f"Mode: {summary['mode']}")
        print(f"Rounds: {summary['total_rounds']}")
        print(f"Total turns: {summary['total_turns']}")
        
        if self.mode != ConversationMode.TEXT_ONLY:
            audio_turns = sum(1 for turn in summary['turns'] if turn['has_audio'])
            print(f"Audio turns: {audio_turns}")
        
        print("\n📊 Turn Summary:")
        for turn in summary['turns']:
            audio_indicator = "🔊" if turn['has_audio'] else "📝"
            print(f"  R{turn['round']} {audio_indicator} {turn['agent']}: {turn['message']}")

async def main():
    """Main function with mode selection"""
    
    print("🚀 AI Roast Battle System V2")
    print("Testing TTS + Audio Playback mode...")
    
    # For now, default to TTS mode to test the new features
    mode = ConversationMode.TTS_PLAYBACK
    
    # Create and run battle
    battle = RoastBattleOrchestrator(mode)
    await battle.run_battle(rounds=6)

if __name__ == "__main__":
    asyncio.run(main())
