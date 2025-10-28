# Quick Setup Guide - Professor Authentication

## 🚀 Quick Start (5 Minutes)

### Step 1: Add Username Column to Database

Run this in your Supabase SQL Editor:

```sql
-- Add username column
ALTER TABLE professors
ADD COLUMN IF NOT EXISTS username VARCHAR(50);

-- Add unique constraint
ALTER TABLE professors
ADD CONSTRAINT professors_username_unique UNIQUE (username);

-- Create index for fast lookups
CREATE INDEX IF NOT EXISTS idx_professors_username ON professors(username);
```

Or run the migration file:
```bash
# Using psql
psql -h your-db-host -U postgres -d postgres -f database/add_username_to_professors.sql
```

### Step 2: Create a Test Account (Optional)

If you want a test account with username, run this in SQL Editor:

```sql
-- Create test professor with username "admin" and password "admin123"
INSERT INTO professors (name, username, email, password_hash, department, created_at)
VALUES (
    'Admin Professor',
    'admin',
    'admin@sfsu.edu',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYfYEYUgTga', -- Password: admin123
    'Computer Science',
    NOW()
)
ON CONFLICT (email) DO NOTHING;
```

### Step 3: Restart Your Backend

```bash
cd D:\sfsu-cs-chatbot\backend
python main.py
```

### Step 4: Test Login

Navigate to `http://localhost:5173/professor` and login with:
- **Username:** `admin`
- **Password:** `admin123`

---

## ✅ Verification Checklist

Run these checks to ensure everything works:

### 1. Database Schema
```sql
-- Check if username column exists
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'professors'
AND column_name = 'username';

-- Should return: username | character varying | YES
```

### 2. Backend Endpoints

Test login with username:
```bash
curl -X POST http://localhost:8000/professor/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

Expected response:
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "professor_name": "Admin Professor",
  "email": "admin@sfsu.edu"
}
```

### 3. Registration Flow

1. Go to `http://localhost:5173/professor/register`
2. Fill in:
   - Name: Test User
   - Username: testuser
   - Email: test@sfsu.edu
   - Department: Computer Science
3. Click "Send OTP"
4. Check backend console for OTP (dev mode)
5. Enter OTP
6. Set password
7. Complete registration

### 4. Login with New Account

1. Go to `http://localhost:5173/professor`
2. Login with username: `testuser`
3. Should redirect to dashboard

---

## 🔧 Configuration

### Environment Variables (Optional)

Add to `backend/.env`:

```env
# JWT Secret (CHANGE THIS IN PRODUCTION!)
JWT_SECRET=your-super-secret-key-change-in-production

# Email Service (Optional - for OTP emails)
RESEND_API_KEY=re_xxxxxxxxxxxxx
SENDER_EMAIL=noreply@yourdomain.com
```

If you don't set `RESEND_API_KEY`, OTP will be printed to console (dev mode).

---

## 📋 What Changed

### Backend Changes:
1. ✅ `auth.py` - Login accepts username OR email
2. ✅ `main.py` - Registration saves username
3. ✅ `main.py` - Login endpoint updated

### Frontend Changes:
1. ✅ Login page - Username field instead of email
2. ✅ Registration page - Added username field (Step 1)
3. ✅ API client - Sends username in login request

### Database Changes:
1. ✅ Added `username` column to `professors` table
2. ✅ Added unique constraint on `username`
3. ✅ Added index for fast username lookups

---

## 🎯 Testing Scenarios

### Scenario 1: Register New Professor

```
1. Navigate to /professor/register
2. Enter name, username, email, department
3. Click "Send OTP"
4. Receive OTP via email (or console in dev mode)
5. Enter OTP
6. Set password
7. Account created ✅
8. Redirected to login
9. Login with new username
10. Access dashboard ✅
```

### Scenario 2: Login with Username

```
1. Navigate to /professor
2. Enter username: admin
3. Enter password: admin123
4. Click login
5. JWT token stored in localStorage
6. Redirected to dashboard ✅
```

### Scenario 3: Login with Email (Still Works!)

```
1. Navigate to /professor
2. Enter email: admin@sfsu.edu
3. Enter password: admin123
4. Click login
5. JWT token stored in localStorage
6. Redirected to dashboard ✅
```

### Scenario 4: Flag & Correct Response

```
1. Student flags response
2. Professor logs in
3. Goes to dashboard
4. Sees pending correction
5. Approves or corrects
6. Stored in verified_facts ✅
7. Next student query uses verified fact ✅
```

---

## 🐛 Common Issues & Fixes

### Issue: "Username already taken"
**Fix:** Username must be unique. Try a different username.

### Issue: "Column 'username' does not exist"
**Fix:** Run the migration SQL (Step 1 above).

### Issue: OTP not received
**Fix:** Check backend console for OTP in dev mode. OTP is printed there.

### Issue: Can't login with username
**Fix:**
1. Check database has username column
2. Check professor has username set
3. Backend should accept username in login request

### Issue: "Invalid username/email or password"
**Fix:**
- Verify credentials are correct
- Check account exists in database
- Password is correct

---

## 📝 Quick Reference

### Demo Credentials:
```
Username: admin
Password: admin123
(or)
Email: admin@sfsu.edu
Password: admin123
```

### Important URLs:
- Login: `http://localhost:5173/professor`
- Register: `http://localhost:5173/professor/register`
- Dashboard: `http://localhost:5173/professor/dashboard`
- Backend API: `http://localhost:8000`

### Database Tables:
- `professors` - User accounts
- `verified_facts` - Professor-approved answers
- `corrections` - Flagged responses

---

## 🎉 You're All Set!

The authentication system is now fully functional with:
- ✅ Username + password login
- ✅ Email + password login (still works)
- ✅ OTP-based registration
- ✅ JWT authentication
- ✅ Protected professor routes

**Next Steps:**
1. Create your professor account
2. Login and test the dashboard
3. Try the correction workflow
4. Deploy to production!

---

**Need Help?**
- See full guide: `AUTHENTICATION_GUIDE.md`
- See correction workflow: `CORRECTION_WORKFLOW.md`
- Check backend logs for errors
