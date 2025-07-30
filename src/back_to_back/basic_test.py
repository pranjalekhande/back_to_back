#!/usr/bin/env python3
"""
Basic Pipecat Test - Single Agent
Tests OpenAI LLM integration with text input/output
"""

import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Basic test without complex imports first
async def test_openai_connection():
    """Test OpenAI connection independently"""
    try:
        import openai
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("❌ No OpenAI API key found in environment")
            return False
            
        client = openai.OpenAI(api_key=api_key)
        
        # Simple test call
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'Pipecat test successful!'"}],
            max_tokens=50
        )
        
        result = response.choices[0].message.content
        print(f"✅ OpenAI Response: {result}")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI test failed: {e}")
        return False

async def test_pipecat_basic():
    """Test basic Pipecat imports and setup"""
    try:
        # Test core imports
        from pipecat.pipeline.pipeline import Pipeline
        from pipecat.pipeline.task import PipelineTask
        from pipecat.pipeline.runner import PipelineRunner
        from pipecat.frames.frames import TextFrame, EndFrame
        
        print("✅ Pipecat core imports successful")
        
        # Test OpenAI service import
        from pipecat.services.openai import OpenAILLMService
        print("✅ OpenAI service import successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Pipecat basic test failed: {e}")
        return False

async def main():
    """Run foundation tests"""
    print("🧪 Phase 1: Foundation Setup Tests")
    print("=" * 50)
    
    # Test 1: OpenAI Connection
    print("\n1️⃣ Testing OpenAI connection...")
    openai_ok = await test_openai_connection()
    
    # Test 2: Pipecat Imports
    print("\n2️⃣ Testing Pipecat imports...")
    pipecat_ok = await test_pipecat_basic()
    
    # Summary
    print("\n📊 Foundation Test Results:")
    print(f"   OpenAI: {'✅ PASS' if openai_ok else '❌ FAIL'}")
    print(f"   Pipecat: {'✅ PASS' if pipecat_ok else '❌ FAIL'}")
    
    if openai_ok and pipecat_ok:
        print("\n🎉 Foundation setup complete! Ready for Phase 2.")
    else:
        print("\n⚠️  Please fix the failing tests before proceeding.")

if __name__ == "__main__":
    asyncio.run(main())
