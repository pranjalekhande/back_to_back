"""Audio file serving endpoints."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from ..services.tts import TTSService

router = APIRouter(tags=["audio"])


@router.get("/audio/{filename}")
async def serve_audio_file(filename: str) -> FileResponse:
    """Serve generated audio files."""
    tts_service = TTSService()
    audio_path = tts_service.get_audio_file_path(filename)
    
    if not audio_path:
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    return FileResponse(
        path=audio_path,
        media_type="audio/mpeg",
        headers={"Cache-Control": "public, max-age=3600"}  # Cache for 1 hour
    )


@router.post("/audio/cleanup")
async def cleanup_audio_files() -> dict[str, int]:
    """Clean up old audio files (admin endpoint)."""
    tts_service = TTSService()
    cleaned_count = tts_service.cleanup_old_files()
    return {"cleaned_files": cleaned_count}
