"""Quick test to verify Gemini model works"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

print("Testing Gemini API...")
print(f"API Key present: {bool(os.getenv('GEMINI_API_KEY'))}")

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Try the new model name
try:
    print("\nTesting model: gemini-2.0-flash-exp")
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    response = model.generate_content(
        "Say 'Hello, I am working!' in one sentence.",
        generation_config={'temperature': 0.5, 'max_output_tokens': 100}
    )
    print(f"[SUCCESS] Response: {response.text}")
    print("\n*** gemini-2.0-flash-exp is WORKING! ***")
except Exception as e:
    print(f"[FAILED] {e}")

    # Try alternative model names
    alternatives = ['gemini-1.5-flash-latest', 'gemini-1.5-flash-002', 'gemini-1.5-pro']
    for model_name in alternatives:
        try:
            print(f"\nTrying model: {model_name}")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(
                "Say 'Hello!' in one word.",
                generation_config={'temperature': 0.5, 'max_output_tokens': 50}
            )
            print(f"[SUCCESS] Response: {response.text}")
            print(f"\n*** Use this model: {model_name} ***")
            break
        except Exception as e:
            print(f"[FAILED] {str(e)[:100]}")
