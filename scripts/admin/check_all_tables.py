#!/usr/bin/env python3
"""Check ALL tables in the database"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv("backend/.env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

print("=" * 70)
print("CHECKING ALL DATABASE TABLES")
print("=" * 70)

print(f"\nConnecting to: {SUPABASE_URL}")

client = create_client(SUPABASE_URL, SUPABASE_KEY)

# List of tables to check
tables = ["professors", "chat_logs", "corrections", "verified_facts"]

for table_name in tables:
    print(f"\n[Table: {table_name}]")
    try:
        result = client.table(table_name).select("*").limit(5).execute()
        print(f"  Row count: {len(result.data)}")
        if len(result.data) > 0:
            print(f"  First row keys: {list(result.data[0].keys())}")
            if table_name == "professors":
                for prof in result.data:
                    print(f"\n  Professor found:")
                    print(f"    ID: {prof.get('id')}")
                    print(f"    Name: {prof.get('name')}")
                    print(f"    Username: {prof.get('username')}")
                    print(f"    Email: {prof.get('email')}")
                    print(f"    Password: {prof.get('password_hash')}")
    except Exception as e:
        print(f"  ERROR: {e}")

print("\n" + "=" * 70)
