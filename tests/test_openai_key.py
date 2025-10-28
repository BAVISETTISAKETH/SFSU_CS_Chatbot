"""Test OpenAI API key"""
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

print("Testing OpenAI API key...")
print(f"API Key found: {bool(os.getenv('OPENAI_API_KEY'))}")
print(f"API Key starts with: {os.getenv('OPENAI_API_KEY', '')[:20]}...")

try:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    print("\nTesting API call...")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Say 'API is working!'"}],
        max_tokens=10
    )

    print(f"\nSUCCESS! Response: {response.choices[0].message.content}")
    print("\nYour OpenAI API is working perfectly!")

except Exception as e:
    print(f"\nERROR: {e}")
    error_str = str(e)

    if "billing" in error_str.lower():
        print("\n❌ ISSUE: Billing not set up")
        print("SOLUTION: Go to https://platform.openai.com/settings/organization/billing")
        print("          Add a payment method to activate your API key")
    elif "quota" in error_str.lower():
        print("\n❌ ISSUE: Quota exceeded")
        print("SOLUTION: Check your usage at https://platform.openai.com/usage")
    elif "invalid" in error_str.lower() or "authentication" in error_str.lower():
        print("\n❌ ISSUE: Invalid API key")
        print("SOLUTION: Generate a new key at https://platform.openai.com/api-keys")
    elif "rate_limit" in error_str.lower() or "429" in error_str:
        print("\n❌ ISSUE: Rate limit reached")
        print("SOLUTION: Wait a few minutes and try again")
