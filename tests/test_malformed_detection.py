"""
Test malformed response detection
"""

import sys
import os

# Add parent directory to path to import backend modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.llm import LLMService

# Initialize LLM service (just for the detection function)
llm = LLMService()

# Test cases - these are actual malformed responses the user is seeing
test_cases = [
    ("@q" * 500, "Pattern: @q@q@q..."),  # The actual pattern from user
    ("H(" * 500, "Pattern: H(H(H(..."),  # The actual pattern from user
    ("abc" * 100, "Pattern: abcabcabc..."),
    ("Hello, this is a normal response with good content about SFSU.", "Normal response"),
    ("", "Empty string"),
    ("x" * 1000, "Single character repeated"),
]

print("="*80)
print("MALFORMED RESPONSE DETECTION TEST")
print("="*80)

for text, description in test_cases:
    is_malformed = llm._is_malformed_response(text)
    status = "[MALFORMED]" if is_malformed else "[OK]"

    print(f"\n{status} - {description}")
    print(f"  Length: {len(text)} chars")
    print(f"  Preview: {text[:60]}...")
    print(f"  Detected as malformed: {is_malformed}")

print("\n" + "="*80)
print("EXPECTED RESULTS:")
print("="*80)
print("[MALFORMED] - Pattern: @q@q@q... (should be TRUE)")
print("[MALFORMED] - Pattern: H(H(H(... (should be TRUE)")
print("[MALFORMED] - Pattern: abcabcabc... (should be TRUE)")
print("[OK] - Normal response (should be FALSE)")
print("[MALFORMED] - Empty string (should be TRUE)")
print("[MALFORMED] - Single character repeated (should be TRUE)")
