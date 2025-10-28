# Debug Login Issues - Step by Step

## 🔍 Issue: "Invalid username/email or password"

Let's figure out what's wrong. Follow these steps:

---

## Step 1: Check if Backend is Running

In your backend terminal, you should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Test the backend API:**
1. Open a new browser tab
2. Go to: http://localhost:8000
3. You should see:
```json
{
  "status": "online",
  "service": "SFSU CS Chatbot API",
  "version": "2.0.0",
  "features": ["RAG", "Web Search", "Professor Corrections"]
}
```

If you DON'T see this, the backend isn't running properly.

---

## Step 2: Check Database Migration (Username Column)

The most common issue is the **username column doesn't exist yet**.

### Check if username column exists:

1. Go to Supabase: https://supabase.com
2. Click "SQL Editor"
3. Run this query:

```sql
-- Check if username column exists
SELECT column_name
FROM information_schema.columns
WHERE table_name = 'professors'
AND column_name = 'username';
```

**Expected Result:**
```
column_name
-----------
username
```

**If you get NO RESULTS**, the username column doesn't exist. Run this:

```sql
-- Add username column
ALTER TABLE professors
ADD COLUMN IF NOT EXISTS username VARCHAR(50);

-- Add unique constraint
ALTER TABLE professors
ADD CONSTRAINT professors_username_unique UNIQUE (username);

-- Create index
CREATE INDEX IF NOT EXISTS idx_professors_username ON professors(username);
```

---

## Step 3: Check if Admin Account Exists

### Option A: Check with username field

Run this in Supabase SQL Editor:
```sql
SELECT id, name, username, email
FROM professors
WHERE username = 'admin' OR email = 'admin@sfsu.edu';
```

**Expected Result:**
```
 id |      name       | username |      email
----+-----------------+----------+----------------
  1 | Admin Professor | admin    | admin@sfsu.edu
```

### Option B: If username column exists but account has no username

If you see this:
```
 id |      name       | username |      email
----+-----------------+----------+----------------
  1 | Admin Professor | (null)   | admin@sfsu.edu
```

The account exists but doesn't have a username. Fix it:

```sql
UPDATE professors
SET username = 'admin',
    password_hash = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYfYEYUgTga'
WHERE email = 'admin@sfsu.edu';
```

### Option C: If account doesn't exist at all

```sql
INSERT INTO professors (name, username, email, password_hash, department, created_at)
VALUES (
    'Admin Professor',
    'admin',
    'admin@sfsu.edu',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYfYEYUgTga',
    'Computer Science',
    NOW()
)
ON CONFLICT (email) DO UPDATE SET
    username = EXCLUDED.username,
    password_hash = EXCLUDED.password_hash;
```

---

## Step 4: Check Backend Logs

When you try to login, check your **backend terminal** for errors:

**Good output (login attempt):**
```
INFO:     127.0.0.1:xxxxx - "POST /professor/login HTTP/1.1" 200 OK
```

**Bad output (errors):**
```
❌ Authentication error: column "username" does not exist
❌ Error searching professors: ...
```

If you see errors, copy them and we'll fix them.

---

## Step 5: Test Login via API (Bypass Frontend)

Let's test if the backend login works directly:

### Using Browser:
1. Install a REST client extension (like "Thunder Client" or "REST Client" for VS Code)
2. Or use an online tool: https://reqbin.com/

### Make this API call:

**Endpoint:** `POST http://localhost:8000/professor/login`

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Expected Response (Success):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "professor_name": "Admin Professor",
  "email": "admin@sfsu.edu"
}
```

**Error Response (Account not found):**
```json
{
  "detail": "Invalid username/email or password"
}
```

---

## Step 6: Check Network Tab in Browser

1. Open the login page: http://localhost:5173/professor
2. Press **F12** to open Developer Tools
3. Go to **Network** tab
4. Try to login
5. Look for a request to `/professor/login`
6. Click on it and check:
   - **Request Payload**: Should show `{"username": "admin", "password": "admin123"}`
   - **Response**: What error message do you see?

---

## Step 7: Common Issues & Solutions

### Issue 1: "Column 'username' does not exist"
**Solution:** Run the migration SQL from Step 2

### Issue 2: Account exists but no username
**Solution:** Update account with username (Step 3, Option B)

### Issue 3: Wrong password hash
The password hash must be EXACTLY:
```
$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYfYEYUgTga
```

**Verify in database:**
```sql
SELECT username, LEFT(password_hash, 20) as password_preview
FROM professors
WHERE username = 'admin';
```

Should show:
```
 username | password_preview
----------+------------------
 admin    | $2b$12$LQv3c1yqBWVH
```

### Issue 4: Backend not connected to database
Check backend terminal for:
```
[OK] Database: True
```

If it says `False`, check your `.env` file has correct Supabase credentials.

---

## Step 8: Fresh Start (Nuclear Option)

If nothing works, let's create a completely new account:

```sql
-- Delete old admin account
DELETE FROM professors WHERE email = 'admin@sfsu.edu';

-- Create fresh account
INSERT INTO professors (name, username, email, password_hash, department, created_at)
VALUES (
    'Test Admin',
    'testadmin',
    'testadmin@sfsu.edu',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYfYEYUgTga',
    'Computer Science',
    NOW()
);
```

Then login with:
- Username: `testadmin`
- Password: `admin123`

---

## Quick Diagnostic Checklist

Run through this checklist:

- [ ] Backend server running (http://localhost:8000 works)
- [ ] Frontend server running (http://localhost:5173 works)
- [ ] Username column exists in professors table
- [ ] Admin account exists in database
- [ ] Admin account has username = 'admin'
- [ ] Admin account has correct password_hash
- [ ] Backend logs show POST request when trying to login
- [ ] No errors in backend logs
- [ ] Browser Network tab shows request to /professor/login

---

## 🔧 **What to Do Next:**

1. **Run the SQL queries above** to check your database
2. **Check the results** and tell me:
   - Does the username column exist?
   - Does the admin account exist?
   - Does it have a username?
   - What do you see in the backend logs when you try to login?

3. **Copy and paste:**
   - Any error messages from backend terminal
   - The SQL query results
   - The Network tab response from browser

I'll help you fix it! 🚀
