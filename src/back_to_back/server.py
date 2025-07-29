"""Development server script."""

import uvicorn

from .app import app

if __name__ == "__main__":
    uvicorn.run(
        "back_to_back.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
