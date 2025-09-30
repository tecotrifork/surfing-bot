#!/usr/bin/env python3
"""
Simple test script to verify the web UI works
"""

import os
import sys

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_bot_initialization():
    """Test if the bot can be initialized properly"""
    try:
        print("🧪 Testing bot initialization...")
        from gpt import SurfingConditionsBot
        bot = SurfingConditionsBot()
        print("✅ Bot initialized successfully!")
        return True
    except Exception as e:
        print(f"❌ Bot initialization failed: {e}")
        return False

def test_simple_query():
    """Test a simple query"""
    try:
        print("🧪 Testing simple query...")
        from gpt import SurfingConditionsBot
        bot = SurfingConditionsBot()
        
        # Test a simple query
        response = bot.chat_with_user("Hello")
        print(f"✅ Query successful! Response length: {len(response)}")
        print(f"📝 First 100 chars: {response[:100]}...")
        return True
    except Exception as e:
        print(f"❌ Query failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🏄‍♂️ Testing Surfing Conditions Bot Web UI Components")
    print("=" * 50)
    
    # Test bot initialization
    if not test_bot_initialization():
        print("\n❌ Bot initialization failed. Please check your config.py and API keys.")
        sys.exit(1)
    
    # Test simple query
    if not test_simple_query():
        print("\n❌ Simple query failed. Please check your API keys and internet connection.")
        sys.exit(1)
    
    print("\n✅ All tests passed! The web UI should work correctly.")
    print("🚀 You can now start the web server with: python3 app.py")
