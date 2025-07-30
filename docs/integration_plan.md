# Integration Plan: Our AI Roast System + Existing Backend/Frontend

## 🎯 Goal: "Boxes Talking to Each Other"
Integrate our working AI roast battle system with their FastAPI backend and React frontend.

## 📋 Current State Analysis

### **Their System** ✅
- **FastAPI backend** with WebSocket support
- **React frontend** with animated faces  
- **Service architecture** (conversation, llm, tts, session)
- **Models** for SpeakerType, ConversationPhase, etc.
- **Redis integration** for sessions
- **TTS service** (placeholder implementation)

### **Our System** ✅
- **Working AI conversation engine** (6-round progression)
- **Real ElevenLabs TTS** integration 
- **Real audio playback** with pygame
- **Modular architecture** (conversation engine, audio services)
- **Battle orchestrator** for complete flows

## 🔄 Integration Strategy: Surgical & Modular

### **Phase 1: Backend Integration** (30 mins)
Replace their conversation/TTS services with our working implementations.

#### **Step 1.1: Replace TTS Service**
- **File**: `src/back_to_back/services/tts.py`
- **Action**: Replace with our `ElevenLabsTTSService`
- **Benefit**: Real audio instead of mock

#### **Step 1.2: Replace Conversation Logic**
- **File**: `src/back_to_back/services/conversation.py`
- **Action**: Integrate our `ConversationEngine` 
- **Benefit**: Real 6-round roast battle

#### **Step 1.3: Update Models**
- **File**: `src/back_to_back/models.py`
- **Action**: Add our conversation modes/phases
- **Benefit**: Support our roast progression

### **Phase 2: API Integration** (20 mins)
Expose our system through their existing endpoints.

#### **Step 2.1: WebSocket Integration**
- **File**: `src/back_to_back/routers/websocket.py`
- **Action**: Connect to our battle orchestrator
- **Benefit**: Real-time battle streaming

#### **Step 2.2: Chat API Updates**
- **File**: `src/back_to_back/routers/chat.py`  
- **Action**: Route to our conversation engine
- **Benefit**: RESTful access to battles

### **Phase 3: Frontend Integration** (10 mins)
Connect React app to working backend.

#### **Step 3.1: WebSocket Client**
- **File**: `faces-zakir/src/App.js`
- **Action**: Connect to WebSocket for real-time updates
- **Benefit**: Live conversation display

#### **Step 3.2: Audio Playback**
- **File**: `faces-zakir/src/App.js`
- **Action**: Add HTML5 audio for TTS playback
- **Benefit**: Browser audio playback

## 🛠️ Implementation Steps

### **Step 1: Restore Our Code**
```bash
git checkout pipecat-framework-setup
git stash pop
# Copy our files to main branch
```

### **Step 2: Surgical TTS Replacement**
Replace their mock TTS with our working ElevenLabs implementation:

```python
# Replace: src/back_to_back/services/tts.py
from ..audio.audio_services import ElevenLabsTTSService
```

### **Step 3: Conversation Engine Integration**
Replace their conversation logic with our battle system:

```python
# Replace: src/back_to_back/services/conversation.py
from ..core.conversation_engine import ConversationEngine, ConversationMode
```

### **Step 4: WebSocket Streaming**
Connect WebSocket to our orchestrator:

```python
# Update: src/back_to_back/routers/websocket.py
from ..roast_battle_v2 import RoastBattleOrchestrator
```

### **Step 5: Frontend Connection**
Connect React to WebSocket for live updates:

```javascript
// Update: faces-zakir/src/App.js
const ws = new WebSocket('ws://localhost:8000/ws');
```

## 🎯 Expected Result

### **Backend API**
- `POST /api/v1/chat/init` - Start new roast battle
- `POST /api/v1/chat/send` - Trigger next round  
- `WS /ws` - Real-time battle streaming
- `GET /audio/{filename}` - Serve TTS audio files

### **Frontend Experience**
- **Two animated faces** representing AMP vs Claude
- **Real-time conversation** text display
- **Audio playback** of roast battle
- **Visual indicators** for speaking agent

### **Flow**
1. User clicks "Start Battle"
2. Backend creates session with our ConversationEngine
3. WebSocket streams real-time battle progress
4. Frontend displays conversation + plays audio
5. Faces animate based on who's speaking

## 🔧 File Mapping

### **Files to Modify**
```
src/back_to_back/
├── services/
│   ├── tts.py              # Replace with our ElevenLabs
│   └── conversation.py     # Integrate our ConversationEngine
├── routers/
│   └── websocket.py        # Connect to our orchestrator
└── models.py              # Add our conversation phases

faces-zakir/src/
└── App.js                 # Add WebSocket + audio
```

### **Files to Copy**
```
src/back_to_back/
├── core/                  # Our conversation engine
├── audio/                 # Our audio services  
└── roast_battle_v2.py    # Our orchestrator
```

## ⚡ Quick Start Commands

```bash
# 1. Get our code
git checkout pipecat-framework-setup
git stash pop

# 2. Copy to main
git checkout main
cp -r [our files] src/back_to_back/

# 3. Install dependencies  
uv sync

# 4. Start backend
python -m back_to_back.server

# 5. Start frontend
cd faces-zakir && npm start
```

## 🎪 Demo Ready Features

After integration:
- ✅ **Real AI roast battle** (6 rounds, flirty → savage)
- ✅ **High-quality TTS** (ElevenLabs voices)  
- ✅ **Animated faces** (React components)
- ✅ **Real-time streaming** (WebSocket)
- ✅ **Audio playback** (Browser audio)
- ✅ **Professional UI** (Existing React app)

**Time Estimate: 60 minutes total**
**Result: Production-ready demo with real AI conversations!**
