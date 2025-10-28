-- Add username field to professors table
-- This allows professors to login with username instead of email

-- Step 1: Add username column (nullable first)
ALTER TABLE professors
ADD COLUMN IF NOT EXISTS username VARCHAR(50);

-- Step 2: Add unique constraint on username
ALTER TABLE professors
ADD CONSTRAINT professors_username_unique UNIQUE (username);

-- Step 3: Create index for fast username lookups
CREATE INDEX IF NOT EXISTS idx_professors_username ON professors(username);

-- Optional: Update existing professors with temporary usernames (if any exist)
-- You can run this to give existing professors usernames based on their email
-- UPDATE professors
-- SET username = SPLIT_PART(email, '@', 1)
-- WHERE username IS NULL;

-- Step 4: Make username NOT NULL after populating (optional, run after migration)
-- ALTER TABLE professors
-- ALTER COLUMN username SET NOT NULL;

-- Verify the changes
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'professors'
ORDER BY ordinal_position;
