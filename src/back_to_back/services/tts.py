"""Text-to-Speech service."""

import os
import tempfile
import uuid
from pathlib import Path
from typing import Optional

from openai import AsyncOpenAI

from ..models import SpeakerType


class TTSService:
    """Service for text-to-speech synthesis."""
    
    def __init__(self):
        # Initialize OpenAI client for TTS
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.client = AsyncOpenAI(api_key=api_key)
        
        # Configure voice mapping for different speakers
        self.voice_mapping = {
            SpeakerType.AGENT_1: "alloy",    # Default voice for agent 1
            SpeakerType.AGENT_2: "echo",     # Different voice for agent 2
            SpeakerType.HUMAN: "nova",       # Voice for human (if TTS needed)
        }
        
        # Configure audio storage
        self.audio_dir = Path(tempfile.gettempdir()) / "back_to_back_audio"
        self.audio_dir.mkdir(exist_ok=True)
        
        # Audio file TTL (in seconds) - files older than this will be cleaned up
        self.audio_ttl = 3600 * 2  # 2 hours
    
    async def synthesize_speech(
        self, text: str, speaker: SpeakerType
    ) -> Optional[str]:
        """
        Synthesize speech from text and return the audio file URL.
        
        Args:
            text: Text to synthesize
            speaker: Speaker type to determine voice
            
        Returns:
            URL/path to the generated audio file, or None if synthesis fails
        """
        if not text or not text.strip():
            return None
        
        try:
            # Get voice for speaker
            voice = self.voice_mapping.get(speaker, "alloy")
            
            # Generate unique filename
            audio_filename = f"{uuid.uuid4()}.mp3"
            audio_path = self.audio_dir / audio_filename
            
            # Call OpenAI TTS API
            response = await self.client.audio.speech.create(
                model="tts-1",  # Faster model for real-time use
                voice=voice,
                input=text[:1000],  # Limit text length for TTS
                response_format="mp3",
            )
            
            # Save audio file
            with open(audio_path, "wb") as f:
                async for chunk in response.iter_bytes():
                    f.write(chunk)
            
            # Return relative URL (frontend will need to handle serving)
            return f"/audio/{audio_filename}"
            
        except Exception as e:
            # Log error (in production, use proper logging)
            print(f"TTS Error: {str(e)}")
            return None
    
    def cleanup_old_files(self) -> int:
        """
        Clean up old audio files to prevent disk space issues.
        
        Returns:
            Number of files cleaned up
        """
        import time
        
        if not self.audio_dir.exists():
            return 0
        
        current_time = time.time()
        cleaned_count = 0
        
        for audio_file in self.audio_dir.glob("*.mp3"):
            try:
                file_age = current_time - audio_file.stat().st_mtime
                if file_age > self.audio_ttl:
                    audio_file.unlink()
                    cleaned_count += 1
            except (OSError, FileNotFoundError):
                # File might have been deleted by another process
                continue
        
        return cleaned_count
    
    def get_audio_file_path(self, filename: str) -> Optional[Path]:
        """
        Get the full path to an audio file by filename.
        
        Args:
            filename: Audio filename (e.g., "uuid.mp3")
            
        Returns:
            Path to the audio file if it exists, None otherwise
        """
        audio_path = self.audio_dir / filename
        if audio_path.exists() and audio_path.suffix == ".mp3":
            return audio_path
        return None
