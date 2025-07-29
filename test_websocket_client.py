#!/usr/bin/env python3
"""Simple WebSocket client to test the agent conversation endpoint."""

import asyncio
import json
import sys
from urllib.parse import urlencode

import websockets


async def test_agent_conversation():
    """Test the WebSocket agent conversation endpoint."""
    
    # Test parameters
    params = {
        "agent_1_persona": "A charming vampire from the 18th century who loves poetry and classical music",
        "agent_2_persona": "A modern tech startup founder who's obsessed with efficiency and productivity", 
        "scenario": "flirt",
        "max_turns": 6
    }
    
    # Build WebSocket URL
    query_string = urlencode(params)
    uri = f"ws://localhost:8000/ws?{query_string}"
    
    print(f"Connecting to: {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to WebSocket")
            print("🎭 Starting agent conversation...")
            print("-" * 50)
            
            # Listen for messages from the server
            async for message in websocket:
                try:
                    # Try to parse as JSON first
                    data = json.loads(message)
                    print(f"📡 Received: {data}")
                except json.JSONDecodeError:
                    # If not JSON, treat as plain text
                    print(f"💬 {message}")
                    
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"❌ Connection closed: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("🚀 Testing Back-to-Back Agent Conversation WebSocket")
    asyncio.run(test_agent_conversation())
