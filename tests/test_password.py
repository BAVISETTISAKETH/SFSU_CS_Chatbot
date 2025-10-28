#!/usr/bin/env python3
"""Test password hashing and verification"""

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# The password we want to test
test_password = "admin123"

# The hash currently in the database
hash_from_db = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYfYEYUgTga"

print("=" * 60)
print("PASSWORD VERIFICATION TEST")
print("=" * 60)

print(f"\nPassword to test: '{test_password}'")
print(f"Hash from database: {hash_from_db}")

# Test verification
try:
    result = pwd_context.verify(test_password, hash_from_db)
    print(f"\nVerification result: {result}")

    if result:
        print("[SUCCESS] Password 'admin123' matches the hash!")
    else:
        print("[FAILED] Password 'admin123' does NOT match the hash!")

except Exception as e:
    print(f"[ERROR] during verification: {e}")

print("\n" + "=" * 60)
print("GENERATING NEW HASH FOR 'admin123'")
print("=" * 60)

# Generate a fresh hash for admin123
new_hash = pwd_context.hash(test_password)
print(f"\nNew hash for 'admin123': {new_hash}")

# Verify the new hash works
new_result = pwd_context.verify(test_password, new_hash)
print(f"New hash verification: {new_result}")

if new_result:
    print("\n[SUCCESS] The NEW hash works correctly!")
    print("\nSQL to update database:")
    print(f"UPDATE professors SET password_hash = '{new_hash}' WHERE username = 'admin';")
