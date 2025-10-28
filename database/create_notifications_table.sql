-- Create notifications table for student notifications
-- Students get notified when professors review their flagged corrections

CREATE TABLE IF NOT EXISTS notifications (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,
    correction_id BIGINT REFERENCES corrections(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR(50) NOT NULL CHECK (type IN ('correction_approved', 'correction_rejected', 'correction_edited')),
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for faster session lookups
CREATE INDEX IF NOT EXISTS notifications_session_id_idx ON notifications(session_id);

-- Index for filtering unread notifications
CREATE INDEX IF NOT EXISTS notifications_is_read_idx ON notifications(is_read);

-- Index for sorting by date
CREATE INDEX IF NOT EXISTS notifications_created_at_idx ON notifications(created_at DESC);

-- Composite index for common query (session + unread)
CREATE INDEX IF NOT EXISTS notifications_session_unread_idx ON notifications(session_id, is_read);

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ Notifications table created successfully!';
    RAISE NOTICE '📬 Students will now be notified when professors review their flagged responses';
END $$;
