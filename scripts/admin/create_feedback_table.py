"""
Create feedback table in Supabase database
"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def create_feedback_table():
    """Create the feedback table if it doesn't exist."""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        print("[ERROR] SUPABASE_URL and SUPABASE_KEY must be set in .env")
        return

    client = create_client(supabase_url, supabase_key)

    # SQL to create feedback table
    sql = """
    CREATE TABLE IF NOT EXISTS feedback (
        id SERIAL PRIMARY KEY,
        session_id TEXT,
        message_id TEXT,
        query TEXT NOT NULL,
        response TEXT NOT NULL,
        feedback_type TEXT NOT NULL CHECK (feedback_type IN ('thumbs_up', 'thumbs_down')),
        created_at TIMESTAMPTZ DEFAULT NOW()
    );

    -- Create index for faster queries
    CREATE INDEX IF NOT EXISTS idx_feedback_created_at ON feedback(created_at DESC);
    CREATE INDEX IF NOT EXISTS idx_feedback_type ON feedback(feedback_type);
    CREATE INDEX IF NOT EXISTS idx_feedback_session ON feedback(session_id);
    """

    print("[INFO] Creating feedback table...")

    try:
        # Execute the SQL (Note: Supabase Python client doesn't directly support raw SQL)
        # You'll need to run this SQL in Supabase SQL Editor manually or use a different approach
        print("""
        [WARNING] Please run the following SQL in your Supabase SQL Editor:

        CREATE TABLE IF NOT EXISTS feedback (
            id SERIAL PRIMARY KEY,
            session_id TEXT,
            message_id TEXT,
            query TEXT NOT NULL,
            response TEXT NOT NULL,
            feedback_type TEXT NOT NULL CHECK (feedback_type IN ('thumbs_up', 'thumbs_down')),
            created_at TIMESTAMPTZ DEFAULT NOW()
        );

        CREATE INDEX IF NOT EXISTS idx_feedback_created_at ON feedback(created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_feedback_type ON feedback(feedback_type);
        CREATE INDEX IF NOT EXISTS idx_feedback_session ON feedback(session_id);
        """)

        print("[SUCCESS] SQL provided above. Please copy and run in Supabase SQL Editor.")

    except Exception as e:
        print(f"[ERROR] Error: {e}")

if __name__ == "__main__":
    create_feedback_table()
