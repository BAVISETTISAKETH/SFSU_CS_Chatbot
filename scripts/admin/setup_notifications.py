"""
Setup script to add notifications system to the database.
Run this once to update your Supabase database schema.
"""

import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

def setup_notifications():
    """Setup notifications table and update corrections table."""

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        print("❌ ERROR: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
        return

    client = create_client(supabase_url, supabase_key)

    print("\n🚀 Setting up notifications system...")
    print("=" * 60)

    # Note: These SQL commands need to be run manually in Supabase SQL Editor
    # because the Python client doesn't support ALTER TABLE directly

    sql_commands = """
-- Step 1: Add session_id column to corrections table if it doesn't exist
ALTER TABLE corrections ADD COLUMN IF NOT EXISTS session_id TEXT;

-- Step 2: Create notifications table
CREATE TABLE IF NOT EXISTS notifications (
    id BIGSERIAL PRIMARY KEY,
    session_id TEXT NOT NULL,
    correction_id BIGINT REFERENCES corrections(id),
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    type TEXT NOT NULL,  -- 'correction_approved', 'correction_rejected', 'correction_edited'
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Step 3: Create index on session_id for fast queries
CREATE INDEX IF NOT EXISTS idx_notifications_session_id ON notifications(session_id);
CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON notifications(is_read);
CREATE INDEX IF NOT EXISTS idx_corrections_session_id ON corrections(session_id);

-- Step 4: Create function to match notifications (similar to match_documents)
CREATE OR REPLACE FUNCTION match_notifications(
    p_session_id TEXT,
    match_count INT DEFAULT 10
)
RETURNS TABLE (
    id BIGINT,
    session_id TEXT,
    correction_id BIGINT,
    title TEXT,
    message TEXT,
    type TEXT,
    is_read BOOLEAN,
    created_at TIMESTAMP WITH TIME ZONE
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        n.id,
        n.session_id,
        n.correction_id,
        n.title,
        n.message,
        n.type,
        n.is_read,
        n.created_at
    FROM notifications n
    WHERE n.session_id = p_session_id
    ORDER BY n.created_at DESC
    LIMIT match_count;
END;
$$;
"""

    print("\n📋 SQL Commands to run in Supabase SQL Editor:")
    print("=" * 60)
    print(sql_commands)
    print("=" * 60)

    print("\n✅ Instructions:")
    print("1. Go to your Supabase project: https://supabase.com/dashboard")
    print("2. Navigate to 'SQL Editor'")
    print("3. Create a new query")
    print("4. Copy and paste the SQL commands above")
    print("5. Click 'Run' to execute")
    print("\n⚠️  Note: This is a one-time setup. Run it only once!")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    setup_notifications()
