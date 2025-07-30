# Our AI Roast Battle System - Documentation

## 🎯 What We Built

### **Core System: AI Roast Battle**
Two AI agents (AMP Code vs Claude Code) have a 6-round conversation that progresses from flirty → teasing → savage roasting, with full audio synthesis and playback.

## 🏗️ Architecture Overview

### **1. Modular Conversation Engine** (`core/conversation_engine.py`)
- **Purpose**: Core LLM conversation logic, mode-agnostic
- **Features**:
  - 6-round prompt progression per agent
  - Conversation history management
  - Multiple conversation modes (TEXT_ONLY, TTS_PLAYBACK, FULL_AUTOMATION)
  - Pluggable audio service integration

### **2. Audio Services** (`audio/audio_services.py`)
- **Purpose**: Modular TTS/STT implementations
- **Features**:
  - Protocol-based design for easy swapping
  - MockAudioService for testing
  - ElevenLabs TTS integration (working)
  - DeepGram TTS/STT support (placeholder)
  - Real audio playback with pygame

### **3. Battle Orchestrator** (`roast_battle_v2.py`)
- **Purpose**: Coordinates conversation and audio based on mode
- **Features**:
  - Mode switching (text-only vs audio)
  - Turn-based conversation management
  - Audio generation and playback coordination
  - Battle summary and statistics

## 🎭 AI Agent Design

### **AMP Code Personality**
- **Rounds 1-2**: Charming, flirty, nerdy compliments
- **Rounds 3-4**: Teasing with programming metaphors  
- **Rounds 5-6**: Savage roastmaster with coding insults

### **Claude Code Personality**
- **Rounds 1-2**: Witty, slightly smug "straight man"
- **Rounds 3-4**: Pushing back with clever remarks
- **Rounds 5-6**: Full roastmaster mode with brutal burns

## 🔊 Audio Integration

### **Text-to-Speech (Working)**
- **Provider**: ElevenLabs API
- **Quality**: High-quality synthesis (200KB+ per message)
- **Voices**: Different voice IDs for each agent
- **Async**: Non-blocking audio generation

### **Audio Playback (Working)**
- **Method**: Pygame mixer with temporary files
- **Quality**: Real system audio output
- **Error Handling**: Fallback to mock if pygame fails
- **Cleanup**: Automatic temporary file deletion

## 📁 File Structure Created

```
src/back_to_back/
├── core/
│   ├── __init__.py
│   └── conversation_engine.py      # Core conversation logic
├── audio/
│   ├── __init__.py
│   └── audio_services.py          # TTS/STT services
├── basic_test.py                   # Foundation tests
├── roast_battle.py                 # V1 text-only version
└── roast_battle_v2.py             # V2 modular version
```

## 🎯 Current Capabilities

### ✅ **Fully Working**
- **6-round AI conversation** with personality progression
- **Real ElevenLabs TTS** generation
- **Real audio playback** through system speakers
- **Modular architecture** for easy extension
- **Error handling** with fallbacks
- **Conversation history** and context management

### 🔧 **Ready for Extension**
- **STT integration** (architecture in place)
- **Full automation mode** (framework ready)
- **Different voice providers** (pluggable design)
- **Web interface integration** (modular design)

## 🎪 Demo Quality

### **Conversation Quality**
- **Hilarious roasts**: "Your confidence is misplaced as a semicolon in Python"
- **Programming metaphors**: "Memory Leak Lane", "linter on steroids"
- **Perfect progression**: Smooth transition from flirty to savage
- **Context awareness**: Agents respond to each other's messages

### **Audio Quality**
- **Natural voices**: Different personalities per agent
- **Good timing**: Realistic conversation pacing
- **Large files**: 200KB-300KB per message (high quality)
- **Reliable playback**: Works consistently across systems

## 🔌 Integration Points

### **What Can Be Integrated**
1. **API Endpoints**: Expose conversation engine via REST/WebSocket
2. **Frontend**: React components can trigger battles and display results
3. **Real-time**: WebSocket integration for live conversation updates
4. **Audio Streaming**: Stream audio directly to frontend
5. **Session Management**: Persistent conversation sessions

### **Key Classes for Integration**
- `ConversationEngine`: Core conversation logic
- `AudioServiceFactory`: Audio service management
- `RoastBattleOrchestrator`: Complete battle coordination

## 🎯 Next Steps for Integration

1. **Analyze existing backend** structure
2. **Map our services** to their architecture
3. **Create API endpoints** for our conversation engine
4. **Integrate with frontend** for visual representation
5. **Add WebSocket support** for real-time updates

---

**Status**: ✅ **Production Ready** - Core system working with real AI and audio
