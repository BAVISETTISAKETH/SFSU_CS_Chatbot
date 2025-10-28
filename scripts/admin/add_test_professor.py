"""
Add test professor to database
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client
from passlib.context import CryptContext
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
load_dotenv()

if not os.getenv("SUPABASE_URL"):
    load_dotenv()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def add_test_professor():
    """Add test professor: admin@sfsu.edu / admin123"""

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        print("[ERROR] SUPABASE_URL and SUPABASE_KEY must be set in .env")
        return

    client: Client = create_client(supabase_url, supabase_key)

    # Check if professor already exists
    result = client.table("professors").select("id").eq("email", "admin@sfsu.edu").execute()

    if result.data:
        print("[INFO] Test professor already exists!")
        print("Email: admin@sfsu.edu")
        print("Password: admin123")
        return

    # Hash password
    password_hash = pwd_context.hash("admin123")

    # Create professor
    try:
        new_prof = client.table("professors").insert({
            "name": "Admin Professor",
            "email": "admin@sfsu.edu",
            "password_hash": password_hash,
            "department": "Computer Science",
            "created_at": datetime.utcnow().isoformat()
        }).execute()

        print("[SUCCESS] Test professor created!")
        print("Email: admin@sfsu.edu")
        print("Password: admin123")
        print("\nYou can now login with these credentials.")

    except Exception as e:
        print(f"[ERROR] Failed to create professor: {e}")

if __name__ == "__main__":
    add_test_professor()
