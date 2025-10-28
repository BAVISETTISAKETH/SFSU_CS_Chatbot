#!/usr/bin/env python3
"""Insert admin account - trying different methods"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv("backend/.env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

print("=" * 70)
print("INSERTING ADMIN ACCOUNT")
print("=" * 70)

client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Method 1: Try basic insert
print("\n[Method 1] Basic insert...")
try:
    result = client.table("professors").insert({
        "name": "Admin Professor",
        "username": "admin",
        "email": "admin@sfsu.edu",
        "password_hash": "admin123",
        "department": "Computer Science"
    }).execute()
    print("SUCCESS!")
    print(f"Inserted: {result.data}")
except Exception as e:
    print(f"FAILED: {e}")

# Check if it was inserted
print("\n[Verification] Checking for admin account...")
result = client.table("professors").select("*").eq("username", "admin").execute()
if result.data and len(result.data) > 0:
    print("SUCCESS! Admin account found:")
    prof = result.data[0]
    print(f"  ID: {prof['id']}")
    print(f"  Username: {prof['username']}")
    print(f"  Email: {prof['email']}")
    print(f"  Password: {prof['password_hash']}")
else:
    print("FAILED - Account not found")
    print("\nThe issue is Row Level Security (RLS) on the professors table.")
    print("You MUST disable RLS in Supabase dashboard:")
    print("1. Go to https://supabase.com")
    print("2. Click 'Table Editor' -> 'professors'")
    print("3. Click the shield icon and disable RLS")
    print("4. Run this script again")

print("=" * 70)
