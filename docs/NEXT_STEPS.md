# ✅ Next Steps to Get Login Working

## Current Status:
✅ Backend is running on http://0.0.0.0:8000
✅ .env file is configured with Supabase credentials
⏳ Need to test connection and set up database

---

## 🚀 **Step-by-Step Instructions**

### **Step 1: Open Backend in Browser**

1. Open your web browser
2. Go to: **http://localhost:8000**
3. You should see:
```json
{
  "status": "online",
  "service": "SFSU CS Chatbot API",
  "version": "2.0.0",
  "features": ["RAG", "Web Search", "Professor Corrections"]
}
```

**Check your terminal** - you should now see:
```
[*] Starting SFSU CS Chatbot API (Alli)...
[OK] Groq LLM: True
[OK] RAG Service: True
[OK] Web Search: True
[OK] Database: True          ← IMPORTANT!
[SUCCESS] All services ready! Alli is online!
INFO:     127.0.0.1:xxxxx - "GET / HTTP/1.1" 200 OK
```

---

### **Step 2: Add Username Column to Database**

Go to **Supabase** (https://supabase.com):

1. Login to your account
2. Click on your project: **cquhriwiulotrthhvdvy**
3. Click **"SQL Editor"** in the left sidebar
4. Click **"New Query"**
5. Copy and paste this SQL:

```sql
-- Add username column to professors table
ALTER TABLE professors
ADD COLUMN IF NOT EXISTS username VARCHAR(50);

-- Add unique constraint
ALTER TABLE professors
ADD CONSTRAINT professors_username_unique UNIQUE (username);

-- Create index for fast lookups
CREATE INDEX IF NOT EXISTS idx_professors_username ON professors(username);

-- Verify it worked
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'professors'
ORDER BY ordinal_position;
```

6. Click **"Run"** (or press F5)

**Expected Result:**
You should see a list of columns including:
```
column_name    | data_type
---------------+-----------
id             | bigint
name           | text
username       | character varying  ← NEW!
email          | text
password_hash  | text
department     | text
last_login     | timestamp
created_at     | timestamp
```

---

### **Step 3: Create Admin Account**

In the same SQL Editor, run this:

```sql
-- Create admin professor account
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

-- Verify the account was created
SELECT username, email, name
FROM professors
WHERE username = 'admin';
```

**Expected Result:**
```
 username |      email       |      name
----------+------------------+-----------------
 admin    | admin@sfsu.edu   | Admin Professor
```

✅ If you see this, the account is created!

---

### **Step 4: Start Frontend**

Open a **NEW terminal** (don't close the backend terminal):

```bash
cd D:\sfsu-cs-chatbot\frontend
npm run dev
```

**Expected Output:**
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

---

### **Step 5: Test Login**

1. Open browser: **http://localhost:5173/professor**
2. Enter credentials:
   - **Username:** `admin`
   - **Password:** `admin123`
3. Click **"Login to Dashboard"**

**Expected Result:**
✅ Redirected to http://localhost:5173/professor/dashboard
✅ You see the professor dashboard!

**If it works:** 🎉 Success! You're logged in!

**If you get "Invalid username/email or password":**
- Check backend terminal for error messages
- Make sure the SQL queries ran successfully
- Verify the account exists in the database

---

## 🔍 **Troubleshooting**

### Issue: Backend shows errors when I visit localhost:8000

**Look for specific errors in the terminal:**

**Error: "column 'username' does not exist"**
- Solution: Run Step 2 (Add username column)

**Error: "SUPABASE_URL not set"**
- Solution: Make sure .env file exists in backend folder
- We already created it, so this shouldn't happen

**Error: Database connection failed**
- Check your Supabase credentials in .env
- Make sure Supabase project is active

---

### Issue: Frontend shows "Cannot connect to backend"

**Solutions:**
1. Make sure backend is running (terminal shows "Uvicorn running")
2. Make sure you're using http://localhost:5173 (not 5174 or other port)
3. Check if CORS is blocking (open browser console - F12)

---

### Issue: Login still says "Invalid username/email or password"

**Debug steps:**

1. **Verify account exists:**
```sql
SELECT * FROM professors WHERE username = 'admin';
```

2. **Check backend logs** when you click login:
   - Should show: `INFO: "POST /professor/login HTTP/1.1" 200 OK` (success)
   - If shows: `401` → credentials wrong
   - If shows: `500` → server error (check error message)

3. **Check browser console** (F12):
   - Look for network errors
   - Check the response from /professor/login

---

## 📝 **Quick Checklist**

Before testing login, make sure:

- [ ] Backend running (http://localhost:8000 shows JSON)
- [ ] Terminal shows "[OK] Database: True"
- [ ] Username column added to database (Step 2)
- [ ] Admin account created (Step 3)
- [ ] Admin account has username = 'admin'
- [ ] Frontend running (http://localhost:5173)
- [ ] Both terminals are still open and running

---

## 🎯 **Summary**

**Right now, your backend IS running!**

**Next actions (in order):**
1. Open http://localhost:8000 in browser
2. Run the SQL migrations in Supabase
3. Create admin account in Supabase
4. Start frontend
5. Try to login!

**Let me know:**
- Did http://localhost:8000 work?
- Did you see the startup messages in terminal?
- Were you able to run the SQL queries in Supabase?
- Did the account get created?

I'm here to help with each step! 🚀
