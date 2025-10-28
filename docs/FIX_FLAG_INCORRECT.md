# 🔧 Fix "Flag Incorrect" Feature - SQL Migration Required

**Problem**: "Failed to submit flag" error when clicking Submit
**Root Cause**: `corrections` table missing `session_id` column
**Solution**: Run SQL migration in Supabase

---

## 🎯 The Issue

The code tries to insert `session_id` into the `corrections` table:

```python
# backend/services/database.py:215
result = self.client.table("corrections").insert({
    "student_query": query,
    "rag_response": response,
    "category": category,
    "session_id": session_id,  # <- This column doesn't exist!
    "status": "pending"
}).execute()
```

But the `corrections` table schema (from `database/schema.sql`) doesn't have this column!

---

## ✅ The Fix - Run SQL Migration

### Step 1: Open Supabase SQL Editor

1. Go to your Supabase Dashboard: https://supabase.com/dashboard
2. Select your project
3. Click **"SQL Editor"** in the left sidebar
4. Click **"New query"**

---

### Step 2: Copy and Run This SQL

Copy this entire SQL command and paste it into the SQL Editor:

```sql
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
```

---

### Step 3: Click "Run" Button

Click the **"Run"** button in the SQL Editor

**Expected Result**:
```
Success
✅ Added session_id column to corrections table
```

---

## 🧪 Test the Fix

After running the SQL migration:

### Step 1: Restart Frontend (Optional)

```bash
# In Terminal 3 (frontend)
# Press Ctrl+C to stop
cd D:\sfsu-cs-chatbot\frontend
npm run dev
```

Frontend was updated to show better error messages, so restart helps.

---

### Step 2: Test Flag Incorrect

1. Open http://localhost:5173
2. Ask any question (e.g., "What is CS 101?")
3. Click **"Flag as incorrect"** button on the response
4. Enter reason: "Testing the flag feature"
5. Click **"Submit"**

**Expected Result**:
```
✅ Success popup: "Thank you for the feedback! A professor will review this response."
```

**NOT**:
```
❌ Error popup: "Failed to submit flag"
```

---

### Step 3: Verify in Professor Dashboard

1. Go to Professor Dashboard (if you have access)
2. Check **"Pending Corrections"** section
3. **Expected**: Your flagged item appears there

---

## 🔍 Alternative: Verify Column Was Added

To verify the migration worked, run this in Supabase SQL Editor:

```sql
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'corrections'
ORDER BY ordinal_position;
```

**Expected Output** (should include):
```
column_name     | data_type
----------------|------------------
id              | bigint
student_query   | text
rag_response    | text
session_id      | character varying  <- Should be here!
status          | character varying
category        | character varying
...
```

---

## 📋 What the SQL Does

1. **Adds `session_id` column**
   - Type: `VARCHAR(100)`
   - Nullable: Yes (existing rows will have NULL)
   - Purpose: Track which chat session the correction came from

2. **Creates index**
   - Faster lookups when filtering by session
   - Improves Professor Dashboard performance

3. **Safe operation**
   - `IF NOT EXISTS` prevents errors if column already exists
   - Won't affect existing data

---

## 🆘 Troubleshooting

### Issue: "Permission denied" error

**Solution**: Make sure you're using the Supabase dashboard with proper admin access

---

### Issue: "Table corrections does not exist"

**Solution**: Run the full schema first:

1. Open `database/schema.sql`
2. Copy the entire contents
3. Paste into Supabase SQL Editor
4. Click "Run"
5. Then run the migration above

---

### Issue: Still getting "Failed to submit flag" after migration

**Check**:
1. Did the SQL run successfully?
2. Is the backend restarted? (Ctrl+C and restart)
3. Check browser console (F12) for detailed error message
4. Check backend terminal for error logs

---

## 📊 Updated Corrections Table Schema

After migration, your `corrections` table will have:

| Column | Type | Description |
|--------|------|-------------|
| id | BIGINT | Primary key |
| student_query | TEXT | Question student asked |
| rag_response | TEXT | Response that was flagged |
| professor_correction | TEXT | Professor's corrected response |
| status | VARCHAR(20) | pending/approved/corrected/rejected |
| category | VARCHAR(100) | Category of the correction |
| **session_id** | **VARCHAR(100)** | **NEW: Session tracking** |
| priority | INTEGER | Correction priority |
| created_at | TIMESTAMP | When flag was submitted |
| reviewed_at | TIMESTAMP | When professor reviewed it |
| reviewed_by | VARCHAR(255) | Professor who reviewed |
| notes | TEXT | Additional notes |

---

## ✅ Success Checklist

After running migration:

- [ ] SQL migration ran successfully in Supabase
- [ ] Column `session_id` exists in `corrections` table
- [ ] Frontend restarted (optional but recommended)
- [ ] Flag button works without errors
- [ ] Success message appears after submitting flag
- [ ] Flagged item appears in Professor Dashboard

---

## 🎯 Quick Summary

**Problem**: `session_id` column missing from `corrections` table

**Fix**: Run SQL migration in Supabase:
```sql
ALTER TABLE corrections
ADD COLUMN IF NOT EXISTS session_id VARCHAR(100);
```

**Test**: Flag a response and verify no errors

**Status**: ✅ SQL migration ready - Just run it in Supabase!

---

**Migration File**: `database/add_session_id_to_corrections.sql`
**Time Required**: 30 seconds (SQL execution)
**Impact**: None (safe migration, no data loss)

🚀 **Run the SQL in Supabase now to fix the flag feature!**
