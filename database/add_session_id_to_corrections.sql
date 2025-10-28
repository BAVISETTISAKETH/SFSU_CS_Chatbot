-- Add session_id column to corrections table
-- This allows tracking which session a correction came from

ALTER TABLE corrections
ADD COLUMN IF NOT EXISTS session_id VARCHAR(100);

-- Add index for faster session lookups
CREATE INDEX IF NOT EXISTS corrections_session_id_idx ON corrections(session_id);

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ Added session_id column to corrections table';
END $$;
