"""
Quick test script to verify Groq API connection works.
Run this BEFORE deploying to production.
"""

import os
from dotenv import load_dotenv

# Load environment
load_dotenv(dotenv_path="backend/.env")

def test_groq():
    """Test Groq API connection."""

    print("=" * 60)
    print("🧪 Testing Groq API Connection")
    print("=" * 60)

    # Check if API key exists
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        print("❌ FAIL: GROQ_API_KEY not found in backend/.env")
        print("   → Get your API key from: https://console.groq.com/keys")
        print("   → Add to backend/.env: GROQ_API_KEY=your_key_here")
        return False

    print(f"✅ GROQ_API_KEY found: {api_key[:20]}...")

    # Test actual API call
    try:
        print("\n📡 Testing API call to Groq...")
        from groq import Groq

        client = Groq(api_key=api_key)

        # Simple test query
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'Hello from Groq!' if you can read this."}
            ],
            max_tokens=100
        )

        result = response.choices[0].message.content

        print(f"✅ SUCCESS! Groq responded: {result[:100]}")
        print("\n" + "=" * 60)
        print("🎉 Groq API is working correctly!")
        print("=" * 60)
        print("\n✅ You're ready to deploy to production!")
        print("   Next step: Follow DEPLOY_NOW.md")
        return True

    except Exception as e:
        print(f"\n❌ FAIL: Error connecting to Groq")
        print(f"   Error: {str(e)}")
        print("\n🔧 Troubleshooting:")
        print("   1. Check your GROQ_API_KEY is correct")
        print("   2. Verify you have internet connection")
        print("   3. Try regenerating your API key at https://console.groq.com/keys")
        print("   4. Make sure groq package is installed: pip install groq")
        return False

if __name__ == "__main__":
    try:
        success = test_groq()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        exit(1)
