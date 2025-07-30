#!/usr/bin/env python3
"""
Audio Services - Modular TTS/STT implementations
Designed for easy extension and swapping between providers
"""

import os
import asyncio
from typing import Protocol, Optional
from abc import ABC, abstractmethod
import aiohttp
import pygame
import tempfile
from dotenv import load_dotenv

load_dotenv()

class AudioServiceInterface(Protocol):
    """Interface for audio services - ensures consistency across implementations"""
    async def text_to_speech(self, text: str, voice_id: str) -> bytes: ...
    async def speech_to_text(self, audio_data: bytes) -> str: ...

class MockAudioService:
    """Mock audio service for testing without API calls"""
    
    async def text_to_speech(self, text: str, voice_id: str) -> bytes:
        """Mock TTS - returns dummy audio data"""
        print(f"🔊 Mock TTS ({voice_id}): {text[:50]}...")
        # Simulate audio generation delay
        await asyncio.sleep(0.5)
        return b"mock_audio_data_" + text.encode()
    
    async def speech_to_text(self, audio_data: bytes) -> str:
        """Mock STT - returns dummy transcription"""
        print(f"👂 Mock STT: Processing {len(audio_data)} bytes...")
        await asyncio.sleep(0.3)
        return f"transcribed: {audio_data.decode('utf-8', errors='ignore')}"

class ElevenLabsTTSService:
    """ElevenLabs Text-to-Speech implementation"""
    
    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.base_url = "https://api.elevenlabs.io/v1"
        
        # Voice configurations for different agents
        self.voice_mapping = {
            "amp_voice": os.getenv("AMP_VOICE_ID", "default_amp_voice"),
            "claude_voice": os.getenv("CLAUDE_VOICE_ID", "default_claude_voice")
        }
    
    async def text_to_speech(self, text: str, voice_id: str) -> bytes:
        """Convert text to speech using ElevenLabs"""
        if not self.api_key:
            print("⚠️  ElevenLabs API key not found, using mock...")
            return await MockAudioService().text_to_speech(text, voice_id)
        
        try:
            # Map agent voice to actual ElevenLabs voice ID
            actual_voice_id = self.voice_mapping.get(voice_id, voice_id)
            
            # Use default voice if no specific voice configured
            if actual_voice_id.startswith("default_"):
                actual_voice_id = "pNInz6obpgDQGcFmaJgB"  # Default voice
            
            url = f"{self.base_url}/text-to-speech/{actual_voice_id}"
            headers = {
                "Accept": "audio/mpeg", 
                "Content-Type": "application/json",
                "xi-api-key": self.api_key
            }
            
            data = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5
                }
            }
            
            print(f"🔊 ElevenLabs TTS ({voice_id}): {text[:50]}...")
            
            # Make async request with aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, headers=headers) as response:
                    if response.status == 200:
                        audio_data = await response.read()
                        print(f"✅ ElevenLabs TTS successful: {len(audio_data)} bytes")
                        return audio_data
                    else:
                        error_text = await response.text()
                        print(f"❌ ElevenLabs API error {response.status}: {error_text}")
                        return await MockAudioService().text_to_speech(text, voice_id)
                
        except Exception as e:
            print(f"❌ ElevenLabs TTS error: {e}")
            return await MockAudioService().text_to_speech(text, voice_id)
    
    async def speech_to_text(self, audio_data: bytes) -> str:
        """STT not implemented for ElevenLabs, fallback to mock"""
        return await MockAudioService().speech_to_text(audio_data)

class DeepgramTTSService:
    """DeepGram Text-to-Speech implementation"""
    
    def __init__(self):
        self.api_key = os.getenv("DEEPGRAM_API_KEY")
        self.base_url = "https://api.deepgram.com/v1/speak"
        
    async def text_to_speech(self, text: str, voice_id: str) -> bytes:
        """Convert text to speech using DeepGram"""
        if not self.api_key:
            print("⚠️  DeepGram API key not found, using mock...")
            return await MockAudioService().text_to_speech(text, voice_id)
        
        try:
            # DeepGram TTS implementation would go here
            print(f"🔊 DeepGram TTS ({voice_id}): {text[:50]}...")
            # For now, fallback to mock
            return await MockAudioService().text_to_speech(text, voice_id)
            
        except Exception as e:
            print(f"❌ DeepGram TTS error: {e}")
            return await MockAudioService().text_to_speech(text, voice_id)
    
    async def speech_to_text(self, audio_data: bytes) -> str:
        """DeepGram STT implementation - for future full automation"""
        if not self.api_key:
            return await MockAudioService().speech_to_text(audio_data)
        
        try:
            # DeepGram STT implementation would go here
            print(f"👂 DeepGram STT: Processing {len(audio_data)} bytes...")
            # For now, fallback to mock
            return await MockAudioService().speech_to_text(audio_data)
            
        except Exception as e:
            print(f"❌ DeepGram STT error: {e}")
            return await MockAudioService().speech_to_text(audio_data)

class AudioServiceFactory:
    """Factory for creating audio services based on configuration"""
    
    @staticmethod
    def create_service(service_type: str = "mock") -> AudioServiceInterface:
        """Create audio service based on type"""
        if service_type == "elevenlabs":
            return ElevenLabsTTSService()
        elif service_type == "deepgram":
            return DeepgramTTSService()
        elif service_type == "mock":
            return MockAudioService()
        else:
            raise ValueError(f"Unknown audio service type: {service_type}")

class AudioPlayer:
    """Audio playback functionality - separated for modularity"""
    
    _pygame_initialized = False
    
    @classmethod
    def _init_pygame(cls):
        """Initialize pygame mixer once"""
        if not cls._pygame_initialized:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            cls._pygame_initialized = True
    
    @staticmethod
    async def play_audio(audio_data: bytes, voice_id: str):
        """Play audio data using pygame"""
        try:
            AudioPlayer._init_pygame()
            
            print(f"🎵 Playing audio for {voice_id}: {len(audio_data)} bytes")
            
            # Create temporary file for audio
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
                tmp_file.write(audio_data)
                tmp_filename = tmp_file.name
            
            # Load and play audio
            pygame.mixer.music.load(tmp_filename)
            pygame.mixer.music.play()
            
            # Wait for playback to complete
            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.1)
            
            # Cleanup
            os.unlink(tmp_filename)
            print(f"✅ Audio playback complete for {voice_id}")
            
        except Exception as e:
            print(f"❌ Audio playback failed: {e}")
            # Fallback to mock playback
            await asyncio.sleep(2.0)
            print(f"🔇 Mock playback complete for {voice_id}")
    
    @staticmethod
    async def save_audio(audio_data: bytes, filename: str):
        """Save audio to file for debugging/testing"""
        try:
            with open(filename, "wb") as f:
                f.write(audio_data)
            print(f"💾 Audio saved to {filename}")
        except Exception as e:
            print(f"❌ Failed to save audio: {e}")
