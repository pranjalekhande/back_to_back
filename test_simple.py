"""Simple test to check if basic imports work."""

def test_imports():
    """Test basic imports."""
    try:
        from back_to_back.models import SpeakerType, ConversationMode
        print("✓ Models import successfully")
        
        from back_to_back.config import settings
        print("✓ Config import successfully")
        
        print("✓ All basic imports working")
        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False

if __name__ == "__main__":
    test_imports()
