#!/usr/bin/env python3
"""List all tables in Supabase database"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv("backend/.env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

print("=" * 70)
print("LISTING ALL TABLES IN DATABASE")
print("=" * 70)

print(f"\nDatabase: {SUPABASE_URL}")

client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Common table names to try
possible_tables = [
    "professors",
    "professor",
    "users",
    "user",
    "admin",
    "admins",
    "chat_logs",
    "corrections",
    "verified_facts",
    "faculty",
    "accounts"
]

print(f"\nChecking which tables exist and have data:\n")

found_tables = []

for table_name in possible_tables:
    try:
        result = client.table(table_name).select("*").limit(1).execute()
        found_tables.append(table_name)
        count_result = client.table(table_name).select("*", count="exact").execute()
        row_count = count_result.count if hasattr(count_result, 'count') else len(count_result.data)

        print(f"  [OK] {table_name.ljust(20)} - EXISTS ({row_count} rows)")

        # If this looks like a user/professor table, show more details
        if "prof" in table_name.lower() or "user" in table_name.lower() or "admin" in table_name.lower():
            if len(result.data) > 0:
                print(f"      Columns: {list(result.data[0].keys())}")

    except Exception as e:
        if "does not exist" not in str(e).lower() and "relation" not in str(e).lower():
            print(f"  [X] {table_name.ljust(20)} - ERROR: {e}")

print(f"\n{'='*70}")
print(f"Found {len(found_tables)} tables: {', '.join(found_tables)}")
print(f"{'='*70}")

# Now specifically check the professors table
print("\n\nDETAILED CHECK OF 'professors' TABLE:")
print("=" * 70)

try:
    # Get all rows
    result = client.table("professors").select("*").execute()
    print(f"\nTotal rows: {len(result.data)}")

    if len(result.data) > 0:
        print(f"\nAll professors in database:")
        for i, prof in enumerate(result.data, 1):
            print(f"\n  Professor {i}:")
            print(f"    ID: {prof.get('id')}")
            print(f"    Name: {prof.get('name')}")
            print(f"    Username: {prof.get('username')}")
            print(f"    Email: {prof.get('email')}")
            print(f"    Password: {prof.get('password_hash')}")
            print(f"    Department: {prof.get('department')}")
    else:
        print("\n  *** TABLE IS EMPTY - NO PROFESSORS FOUND ***")

except Exception as e:
    print(f"\nERROR accessing professors table: {e}")

print("\n" + "=" * 70)
