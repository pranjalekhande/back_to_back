# AI Roast Battle System - Usage Instructions

## 🚀 Quick Start Guide

### **Prerequisites**
1. **Environment Setup**: Update `.env` file with your API keys
   ```bash
   # Required API keys
   OPENAI_API_KEY=your_openai_key_here
   ELEVENLABS_API_KEY=your_elevenlabs_key_here
   
   # Custom Voice IDs (optional)
   AMP_VOICE_ID=1A6HcAmiRXLCnJSuyoMp    # Avery Moore for AMP Code
   CLAUDE_VOICE_ID=ghGY4Tgpbvfgm5ZSZoo9  # Pat Sirous for Claude Code
   ```

2. **Python Environment**
   ```bash
   # Activate virtual environment
   source .venv/bin/activate
   ```

## 🎭 Method 1: Direct Python Script (Recommended for Testing)

### **Run Roast Battle Directly**
```bash
# Navigate to project directory
cd /Users/pranjal/Documents/hackathon/back_to_back

# Activate environment
source .venv/bin/activate

# Switch to working branch
git checkout pipecat-framework-setup

# Run roast battle (with audio playback)
cd src && python back_to_back/roast_battle_v2.py
```

**What happens:**
- 6-round AMP vs Claude roast battle
- Real ElevenLabs TTS generation
- Audio plays through system speakers
- Complete conversation displayed in terminal

## 🌐 Method 2: FastAPI Server (For API Integration)

### **Start Backend Server**
```bash
# Navigate to project directory
cd /Users/pranjal/Documents/hackathon/back_to_back

# Activate environment
source .venv/bin/activate

# Switch to main branch (has FastAPI server)
git checkout main

# Start server
cd src && python -m back_to_back.server
```

**Server will start on:** `http://localhost:8000`

### **API Endpoints**

#### **Health Check**
```bash
curl http://localhost:8000/health
```
Response: `{"status": "healthy"}`

#### **Start Roast Battle** (if available)
```bash
# 6-round battle
curl -X POST "http://localhost:8000/api/v1/roast-battle?rounds=6"

# 2-round battle (faster testing)
curl -X POST "http://localhost:8000/api/v1/roast-battle?rounds=2"
```

#### **Get Audio File** (after battle)
```bash
# Replace {filename} with actual filename from API response
curl http://localhost:8000/audio/{filename}.mp3 --output audio_file.mp3
```

## 🔧 Troubleshooting

### **Common Issues**

#### **1. Server Not Starting**
```bash
# Check if port 8000 is in use
lsof -ti:8000

# Kill process if needed
kill -9 $(lsof -ti:8000)

# Try different port
cd src && uvicorn back_to_back.app:app --host 0.0.0.0 --port 8001
```

#### **2. Module Not Found**
```bash
# Ensure you're in the right directory and environment
pwd  # Should be /Users/pranjal/Documents/hackathon/back_to_back
source .venv/bin/activate
which python  # Should show .venv/bin/python
```

#### **3. API Endpoint Not Found (404)**
- Switch to `main` branch for FastAPI server
- Or use direct Python script on `pipecat-framework-setup` branch

#### **4. Audio Not Playing**
```bash
# Install pygame if missing
uv add pygame

# Check audio system
python -c "import pygame; pygame.mixer.init(); print('Audio system OK')"
```

## 🎵 Testing Voices

### **Quick Voice Test**
```bash
# Switch to working branch
git checkout pipecat-framework-setup

# Run 2-round battle for quick voice test
cd src && python -c "
import asyncio
from back_to_back.roast_battle_v2 import run_roast_battle
asyncio.run(run_roast_battle(rounds=2))
"
```

### **Voice Configuration Test**
```bash
# Check current voice IDs
grep -E "(AMP_VOICE_ID|CLAUDE_VOICE_ID)" .env

# Test ElevenLabs connection
curl -H "xi-api-key: YOUR_API_KEY" https://api.elevenlabs.io/v1/voices
```

## 📊 Expected Response Format

### **Roast Battle API Response**
```json
{
  "status": "success",
  "rounds": 6,
  "messages": [
    {
      "speaker": "agent_1",
      "text": "Oh, hello there, Claude Code!...",
      "audio_url": "/audio/49c32724-d8cc-4ecb-857a-24e3c2b0dd47.mp3",
      "turn_number": 1,
      "timestamp": "2025-07-30T00:36:32.529499"
    }
  ],
  "total_messages": 12
}
```

## 🚀 React Frontend (Future Integration)

### **Start React App**
```bash
# Navigate to React app
cd faces-zakir

# Install dependencies (if needed)
npm install

# Start development server
npm start
```

**React app runs on:** `http://localhost:3000`

## 📁 Branch Overview

### **`main` Branch**
- ✅ FastAPI server with health endpoints
- ✅ WebSocket support
- ❌ Roast battle endpoint not integrated

### **`pipecat-framework-setup` Branch** 
- ✅ Complete roast battle system
- ✅ ElevenLabs TTS integration
- ✅ Direct Python script execution
- ✅ React frontend (faces-zakir)
- ❌ FastAPI integration incomplete

## 🎯 Quick Commands Summary

```bash
# Test voices with direct script
git checkout pipecat-framework-setup && cd src && python back_to_back/roast_battle_v2.py

# Start FastAPI server  
git checkout main && cd src && python -m back_to_back.server

# Start React frontend
cd faces-zakir && npm start

# Test API (if server running)
curl -X POST "http://localhost:8000/api/v1/roast-battle?rounds=2"
```

---

**For voice testing, use the direct Python script method on `pipecat-framework-setup` branch!**
