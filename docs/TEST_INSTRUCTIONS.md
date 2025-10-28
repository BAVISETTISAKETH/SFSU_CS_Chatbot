# Testing Instructions - Step by Step

## 🧪 Complete Testing Guide

Follow these steps to test your authentication and correction system.

---

## ✅ Pre-Test Checklist

### 1. **Start Backend Server**
```bash
# Open Terminal 1
cd D:\sfsu-cs-chatbot
venv\Scripts\activate
cd backend
python main.py
```

Expected output:
```
[*] Starting SFSU CS Chatbot API (Alli)...
[OK] Groq LLM: True
[OK] RAG Service: True
[OK] Web Search: True
[OK] Database: True
[SUCCESS] All services ready! Alli is online!
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. **Start Frontend Server**
```bash
# Open Terminal 2
cd D:\sfsu-cs-chatbot\frontend
npm run dev
```

Expected output:
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

### 3. **Apply Database Migration**

**Option A: Using Supabase Dashboard**
1. Open https://supabase.com and login
2. Go to your project
3. Click "SQL Editor"
4. Paste this SQL:
```sql
ALTER TABLE professors ADD COLUMN IF NOT EXISTS username VARCHAR(50);
ALTER TABLE professors ADD CONSTRAINT professors_username_unique UNIQUE (username);
CREATE INDEX IF NOT EXISTS idx_professors_username ON professors(username);
```
5. Click "Run"

**Option B: Using psql**
```bash
# From D:\sfsu-cs-chatbot directory
psql -h your-db-host -U postgres -d postgres -f database/add_username_to_professors.sql
```

### 4. **Create Test Professor Account**
Run this in Supabase SQL Editor:
```sql
INSERT INTO professors (name, username, email, password_hash, department, created_at)
VALUES (
    'Test Admin',
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

## 🧪 Test 1: Professor Login

### Steps:
1. Open browser: http://localhost:5173/professor
2. Enter credentials:
   - **Username:** `admin`
   - **Password:** `admin123`
3. Click "Login to Dashboard"

### Expected Results:
- ✅ No error message
- ✅ Redirected to http://localhost:5173/professor/dashboard
- ✅ See dashboard with "Professor Dashboard" header
- ✅ Can see tabs: "Pending Corrections" and "Stats"

### If Login Fails:
**Check Backend Logs:**
- Look for error messages in Terminal 1
- Should see: `[*] POST /professor/login`

**Troubleshooting:**
```bash
# Test login via API
curl -X POST http://localhost:8000/professor/login \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"admin\", \"password\": \"admin123\"}"
```

Expected response:
```json
{
  "access_token": "eyJhbG...",
  "token_type": "bearer",
  "professor_name": "Test Admin",
  "email": "admin@sfsu.edu"
}
```

---

## 🧪 Test 2: Professor Registration

### Steps:

**Step 1: Enter Details**
1. Go to: http://localhost:5173/professor/register
2. Fill in the form:
   - **Full Name:** Test Professor
   - **Username:** testprof (must be unique)
   - **SFSU Email:** testprof@sfsu.edu
   - **Department:** Computer Science
3. Click "Send OTP"

### Expected Results:
- ✅ Success message: "OTP sent to your email!"
- ✅ Progress indicator shows step 2 active (purple dots)
- ✅ OTP form appears

**Check Backend Console:**
```
[EMAIL] OTP sent to testprof@sfsu.edu via Resend
(or)
[DEV MODE] OTP for testprof@sfsu.edu: 123456
```

**Step 2: Verify OTP**
1. Check backend console for OTP (in dev mode)
2. Enter the 6-digit OTP
3. Click "Verify"

### Expected Results:
- ✅ Success message: "Email verified! Now set your password."
- ✅ Progress indicator shows step 3 active
- ✅ Password form appears

**Step 3: Set Password**
1. Enter password: testpass123
2. Confirm password: testpass123
3. Click "Create Account"

### Expected Results:
- ✅ Alert: "Account created successfully! Please login."
- ✅ Redirected to http://localhost:5173/professor
- ✅ Can now login with new credentials

**Verify in Database:**
```sql
SELECT username, email, name FROM professors WHERE username = 'testprof';
```

Should return:
```
 username  |        email        |      name
-----------+---------------------+----------------
 testprof  | testprof@sfsu.edu  | Test Professor
```

---

## 🧪 Test 3: Login with New Account

### Steps:
1. Go to: http://localhost:5173/professor
2. Enter:
   - **Username:** `testprof`
   - **Password:** `testpass123`
3. Click "Login to Dashboard"

### Expected Results:
- ✅ Login successful
- ✅ Redirected to dashboard
- ✅ See "Professor Dashboard" header
- ✅ Token stored in localStorage

**Verify Token:**
Open browser console (F12) and run:
```javascript
localStorage.getItem('professorToken')
```

Should return a JWT token like:
```
"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

## 🧪 Test 4: Correction Workflow (Full Flow)

### Part A: Student Flags Response

1. **Open Student Chat:** http://localhost:5173/chat
2. **Ask a question:** "What is CPT?"
3. **Wait for response**
4. **Click "Flag as incorrect"** button
5. **Enter reason:** "CPT should be Curricular Practical Training, not Computer Programming Technology"
6. **Click "Submit"**

### Expected Results:
- ✅ Alert: "Thank you! A professor will review this response."
- ✅ Correction saved to database

**Verify in Backend Console:**
```
[*] POST /corrections/flag
[OK] Correction created with ID: 1
```

**Verify in Database:**
```sql
SELECT * FROM corrections ORDER BY created_at DESC LIMIT 1;
```

---

### Part B: Professor Reviews Correction

1. **Login as professor:** http://localhost:5173/professor
2. **Go to dashboard**
3. **Click "Pending Corrections" tab**

### Expected Results:
- ✅ See flagged correction
- ✅ Student query displayed
- ✅ Bot response displayed
- ✅ Student reason displayed
- ✅ Three buttons: "Approve", "Correct", "Reject"

---

### Part C: Professor Corrects Response

**Option 1: Approve (Response is correct)**
1. Click "Approve" button
2. Wait for confirmation

**Expected:**
- ✅ Correction removed from pending list
- ✅ Original response stored in `verified_facts` table

**Option 2: Correct (Edit response)**
1. Click "Correct" button
2. Textarea becomes editable
3. Edit the response:
```
CPT (Curricular Practical Training) is work authorization for F-1
international students. It allows students to work in their field of
study while completing their degree. Apply through the International
Programs Office.
```
4. Click "Submit Correction"

**Expected:**
- ✅ Success message
- ✅ Correction removed from pending
- ✅ Edited response stored in `verified_facts` table

**Verify in Database:**
```sql
SELECT * FROM verified_facts ORDER BY created_at DESC LIMIT 1;
```

Should show:
- question: "What is CPT?"
- answer: "CPT (Curricular Practical Training)..."
- verified_by: Your professor email
- embedding: [vector data]

---

### Part D: Student Gets Verified Response

1. **Open new chat or refresh:** http://localhost:5173/chat
2. **Ask similar question:** "Tell me about CPT"
3. **Wait for response**

### Expected Results:
- ✅ Bot returns professor's corrected answer
- ✅ Response should match what professor entered
- ✅ Backend console shows:
```
[VERIFIED FACT] Query: "Tell me about CPT"
[OK] Found verified fact with confidence: 0.89
```

**Verify in Backend Console:**
Should see:
```
[VERIFIED FACT] Returning verified answer
Source: verified_fact
Confidence: 0.89
```

---

## 🧪 Test 5: Login with Email (Alternative)

### Steps:
1. Logout (if logged in)
2. Go to: http://localhost:5173/professor
3. Enter:
   - **Username:** `admin@sfsu.edu` (email instead of username)
   - **Password:** `admin123`
4. Click "Login"

### Expected Results:
- ✅ Login successful
- ✅ Backend accepts email as well as username
- ✅ Redirected to dashboard

---

## 🧪 Test 6: Error Scenarios

### Test Invalid Credentials
1. Go to login page
2. Enter wrong username: `wronguser`
3. Enter any password
4. Click login

**Expected:**
- ✅ Error message: "Invalid username/email or password"
- ✅ Stay on login page

### Test Username Already Taken
1. Go to registration
2. Try to register with username: `admin`
3. Complete OTP verification
4. Try to create account

**Expected:**
- ✅ Error: "Username already taken. Please choose another."

### Test Invalid OTP
1. Go to registration
2. Enter details and request OTP
3. Enter wrong OTP: `000000`
4. Click verify

**Expected:**
- ✅ Error: "Invalid or expired OTP. Please try again."

### Test Expired OTP
1. Request OTP
2. Wait 11 minutes
3. Try to verify

**Expected:**
- ✅ Error: "Invalid or expired OTP"
- ✅ Can click "Resend OTP"

---

## 📊 Testing Checklist

Mark each test as you complete it:

- [ ] Backend server starts successfully
- [ ] Frontend server starts successfully
- [ ] Database migration applied
- [ ] Test professor account created
- [ ] Login with username works
- [ ] Login with email works
- [ ] Registration Step 1 works (send OTP)
- [ ] Registration Step 2 works (verify OTP)
- [ ] Registration Step 3 works (set password)
- [ ] New account created in database
- [ ] Login with new account works
- [ ] Student can flag response
- [ ] Professor sees flagged response
- [ ] Professor can approve response
- [ ] Professor can edit and correct response
- [ ] Verified fact stored in database
- [ ] Student gets verified fact on similar query
- [ ] Invalid credentials show error
- [ ] Duplicate username shows error
- [ ] Invalid OTP shows error

---

## 🐛 Common Issues & Solutions

### Issue: "Failed to send OTP"
**Solution:**
- OTP service working in dev mode
- Check backend console for OTP code
- No email configuration needed for testing

### Issue: "Cannot connect to backend"
**Check:**
- Backend running on port 8000
- No firewall blocking
- .env file has correct Supabase credentials

### Issue: "Username already taken"
**Solution:**
- Try a different username
- Or delete existing user from database:
```sql
DELETE FROM professors WHERE username = 'testprof';
```

### Issue: Correction not showing in dashboard
**Check:**
- Professor is logged in
- Token is valid (check localStorage)
- Correction status is 'pending'
```sql
SELECT * FROM corrections WHERE status = 'pending';
```

### Issue: Verified fact not being retrieved
**Check:**
- Fact was stored:
```sql
SELECT * FROM verified_facts ORDER BY created_at DESC;
```
- Query is similar enough (vector similarity)
- Backend logs show verified fact search

---

## 📝 Testing Notes

**What to Look For:**
1. **Backend Logs:** Every request should be logged
2. **Network Tab:** Check API requests in browser DevTools (F12)
3. **Console Errors:** Any JavaScript errors in browser console
4. **Database State:** Verify data is actually stored

**Performance:**
- Login should be < 1 second
- Registration should be < 2 seconds (excluding OTP email)
- Chat responses should be < 5 seconds
- Dashboard load should be < 2 seconds

---

## ✅ Success Criteria

All tests pass if:
- ✅ Can register new professor account with OTP
- ✅ Can login with username
- ✅ Can login with email
- ✅ Can access professor dashboard
- ✅ Can see pending corrections
- ✅ Can approve/correct flagged responses
- ✅ Verified facts are stored
- ✅ Students receive verified facts on similar queries
- ✅ All data persists in database
- ✅ Errors are handled gracefully

---

**Ready to test? Follow the steps above!** 🚀

If you encounter any issues, check the troubleshooting section or review the backend logs.
