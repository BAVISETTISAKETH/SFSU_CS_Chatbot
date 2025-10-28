#!/usr/bin/env python3
"""Test database connection"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

print("=" * 70)
print("DATABASE CONNECTION TEST")
print("=" * 70)

# Get credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

print(f"\n[1] Environment Variables:")
print(f"    SUPABASE_URL: {SUPABASE_URL}")
print(f"    SUPABASE_KEY: {SUPABASE_KEY[:30]}... (truncated)")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("\n[ERROR] Missing SUPABASE_URL or SUPABASE_KEY!")
    sys.exit(1)

# Test connection
print(f"\n[2] Creating Supabase client...")
try:
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("    SUCCESS - Client created")
except Exception as e:
    print(f"    ERROR - Failed to create client: {e}")
    sys.exit(1)

# Test query to professors table
print(f"\n[3] Testing query to 'professors' table...")
try:
    result = client.table("professors").select("*").execute()
    print(f"    SUCCESS - Query executed")
    print(f"    Found {len(result.data)} professors in database")

    if len(result.data) > 0:
        print(f"\n[4] Professors in database:")
        for prof in result.data:
            print(f"    - ID: {prof.get('id')}")
            print(f"      Name: {prof.get('name')}")
            print(f"      Username: {prof.get('username')}")
            print(f"      Email: {prof.get('email')}")
            print(f"      Password: {prof.get('password_hash')}")
            print()
    else:
        print(f"\n[4] NO PROFESSORS FOUND IN DATABASE!")
        print(f"    The table exists but is EMPTY")

except Exception as e:
    print(f"    ERROR - Query failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test search for specific username
print(f"\n[5] Testing search for username 'admin'...")
try:
    result = client.table("professors").select("*").eq("username", "admin").execute()
    print(f"    Query completed")
    print(f"    Found {len(result.data)} rows")

    if len(result.data) > 0:
        prof = result.data[0]
        print(f"\n    FOUND ADMIN ACCOUNT:")
        print(f"    - ID: {prof.get('id')}")
        print(f"    - Name: {prof.get('name')}")
        print(f"    - Username: {prof.get('username')}")
        print(f"    - Email: {prof.get('email')}")
        print(f"    - Password: {prof.get('password_hash')}")
    else:
        print(f"\n    NO ADMIN ACCOUNT FOUND")

except Exception as e:
    print(f"    ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
