#!/usr/bin/env python3
"""Add admin professor account to database"""

import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv("backend/.env")

# Get Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

print("=" * 60)
print("ADDING ADMIN ACCOUNT TO DATABASE")
print("=" * 60)

# Connect to Supabase
client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Delete existing admin account if any
print("\n[1] Deleting any existing admin accounts...")
try:
    client.table("professors").delete().eq("username", "admin").execute()
    client.table("professors").delete().eq("email", "admin@sfsu.edu").execute()
    print("    - Cleaned up old accounts")
except Exception as e:
    print(f"    - No old accounts to delete: {e}")

# Insert new admin account with plain text password
print("\n[2] Creating new admin account...")
admin_data = {
    "name": "Admin Professor",
    "username": "admin",
    "email": "admin@sfsu.edu",
    "password_hash": "admin123",  # Plain text password
    "department": "Computer Science",
    "created_at": "2025-10-12T00:00:00Z"
}

try:
    result = client.table("professors").insert(admin_data).execute()
    print("    - SUCCESS! Admin account created")
    print(f"    - ID: {result.data[0]['id']}")
except Exception as e:
    print(f"    - ERROR: {e}")

# Verify it was created
print("\n[3] Verifying admin account...")
result = client.table("professors").select("*").eq("username", "admin").execute()

if result.data and len(result.data) > 0:
    prof = result.data[0]
    print("    - SUCCESS! Account verified:")
    print(f"    - ID: {prof['id']}")
    print(f"    - Name: {prof['name']}")
    print(f"    - Username: {prof['username']}")
    print(f"    - Email: {prof['email']}")
    print(f"    - Password: {prof['password_hash']}")
    print(f"    - Department: {prof['department']}")
else:
    print("    - ERROR: Account not found!")

print("\n" + "=" * 60)
print("DONE!")
print("=" * 60)
print("\nYou can now login with:")
print("  Username: admin")
print("  Password: admin123")
print("=" * 60)
