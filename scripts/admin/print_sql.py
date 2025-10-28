"""
Simple script to print the SQL commands for setting up notifications.
No dependencies required - just prints the SQL you need to run in Supabase.
"""

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

-- Step 3: Create indexes for fast queries
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

print("\n" + "=" * 70)
print("📋 COPY THE SQL BELOW AND RUN IT IN SUPABASE")
print("=" * 70)
print(sql_commands)
print("=" * 70)

print("\n✅ INSTRUCTIONS:")
print("=" * 70)
print("1. Go to your Supabase Dashboard: https://supabase.com/dashboard")
print("2. Select your project")
print("3. Click on 'SQL Editor' in the left sidebar")
print("4. Click 'New query' button")
print("5. Copy ALL the SQL commands above (from ALTER TABLE to END;)")
print("6. Paste them into the SQL Editor")
print("7. Click 'Run' button (or press Ctrl+Enter)")
print("8. You should see success messages for each command")
print("\n⚠️  IMPORTANT: This is a ONE-TIME setup. Run it only once!")
print("=" * 70)
print("\nAfter running the SQL, you can test the notification system!")
