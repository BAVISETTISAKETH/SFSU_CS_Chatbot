# Professor Authentication System - Complete Guide

## Overview
This document explains the complete professor authentication system including registration with OTP verification and username/password login.

---

## 🔐 Authentication Flow

### 1️⃣ **Registration Flow (3-Step Process)**

```
Step 1: Enter Details
  ├─ Full Name
  ├─ Username (3-50 characters, unique)
  ├─ SFSU Email (@sfsu.edu required)
  └─ Department

Step 2: Email Verification
  ├─ OTP sent to email
  ├─ Professor enters 6-digit code
  └─ OTP verified (10-minute expiration)

Step 3: Set Password
  ├─ Create password (minimum 6 characters)
  ├─ Confirm password
  └─ Account created in database
```

### 2️⃣ **Login Flow**

```
Login Page
  ├─ Enter Username OR Email
  ├─ Enter Password
  ├─ Backend verifies credentials
  ├─ JWT token generated
  └─ Redirected to Dashboard
```

---

## 📊 Database Schema

### Professors Table
```sql
CREATE TABLE professors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    department VARCHAR(100),
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for fast lookups
CREATE INDEX idx_professors_username ON professors(username);
CREATE INDEX idx_professors_email ON professors(email);
```

### Migration Script
Run the SQL migration to add username field:
```bash
# Apply the migration
psql -h your-supabase-host -U postgres -d postgres -f database/add_username_to_professors.sql
```

Or in Supabase dashboard:
1. Go to SQL Editor
2. Copy contents of `database/add_username_to_professors.sql`
3. Run the script

---

## 🛠️ Implementation Details

### Backend Services

#### 1. **AuthService** (`backend/services/auth.py`)

**Key Functions:**
- `authenticate_professor(username_or_email, password)` - Login with username or email
- `create_access_token(data)` - Generate JWT token
- `verify_token(token)` - Validate JWT token
- `hash_password(password)` - Hash password using bcrypt
- `verify_password(plain_password, hashed_password)` - Verify password

**Example Usage:**
```python
# Login
professor = await auth_service.authenticate_professor("john_doe", "password123")

# Generate token
token = auth_service.create_access_token({
    "email": professor['email'],
    "username": professor['username'],
    "id": professor['id']
})

# Verify token
payload = auth_service.verify_token(token)
```

#### 2. **EmailService** (`backend/services/email.py`)

**Key Functions:**
- `generate_otp()` - Generate 6-digit OTP
- `send_otp_email(email, name)` - Send OTP via Resend API
- `verify_otp(email, otp)` - Verify OTP (max 5 attempts, 10-min expiration)

**OTP Storage:**
```python
{
    "email@sfsu.edu": {
        "otp": "123456",
        "expires_at": datetime,
        "attempts": 0
    }
}
```

**Note:** In production, use Redis or database for OTP storage instead of in-memory dict.

---

## 🌐 API Endpoints

### Registration Endpoints

#### 1. Send OTP
```http
POST /professor/send-otp
Content-Type: application/json

{
  "email": "professor@sfsu.edu",
  "name": "John Doe"
}
```

**Response:**
```json
{
  "message": "OTP sent successfully to your email",
  "dev_otp": "123456"  // Only in dev mode
}
```

#### 2. Verify OTP
```http
POST /professor/verify-otp
Content-Type: application/json

{
  "email": "professor@sfsu.edu",
  "otp": "123456"
}
```

**Response:**
```json
{
  "message": "OTP verified successfully"
}
```

#### 3. Register Professor
```http
POST /professor/register
Content-Type: application/json

{
  "name": "John Doe",
  "username": "johndoe",
  "email": "professor@sfsu.edu",
  "password": "securePassword123",
  "department": "Computer Science",
  "otp": "123456"
}
```

**Response:**
```json
{
  "message": "Account created successfully. Please login."
}
```

**Error Responses:**
- `400` - Invalid OTP, email already registered, or username taken
- `500` - Server error

---

### Login Endpoint

```http
POST /professor/login
Content-Type: application/json

{
  "username": "johndoe",  // Can be username OR email
  "password": "securePassword123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "professor_name": "John Doe",
  "email": "professor@sfsu.edu"
}
```

**Error Responses:**
- `401` - Invalid username/email or password

---

## 🎨 Frontend Implementation

### Registration Page (`frontend/src/pages/ProfessorRegister.jsx`)

**3-Step Process:**

**Step 1: Collect Information**
```jsx
<form onSubmit={handleSendOTP}>
  <input name="name" placeholder="John Doe" />
  <input name="username" placeholder="johndoe" />
  <input name="email" placeholder="professor@sfsu.edu" />
  <select name="department">
    <option>Computer Science</option>
    ...
  </select>
  <button>Send OTP</button>
</form>
```

**Step 2: Verify OTP**
```jsx
<form onSubmit={handleVerifyOTP}>
  <input
    name="otp"
    maxLength="6"
    placeholder="000000"
  />
  <button>Verify</button>
</form>
```

**Step 3: Set Password**
```jsx
<form onSubmit={handleSubmit}>
  <input
    name="password"
    type="password"
    placeholder="At least 6 characters"
  />
  <input
    name="confirmPassword"
    type="password"
    placeholder="Confirm your password"
  />
  <button>Create Account</button>
</form>
```

### Login Page (`frontend/src/pages/ProfessorLogin.jsx`)

```jsx
<form onSubmit={handleSubmit}>
  <input
    name="username"
    placeholder="your_username or professor@sfsu.edu"
  />
  <input
    name="password"
    type="password"
    placeholder="Enter your password"
  />
  <button>Login to Dashboard</button>
</form>
```

---

## 🔒 Security Features

### 1. **Password Hashing**
- Uses **bcrypt** algorithm
- Automatically salted
- One-way hashing (cannot be decrypted)

```python
# Hash password
hashed = pwd_context.hash("password123")

# Verify password
is_valid = pwd_context.verify("password123", hashed)
```

### 2. **JWT Tokens**
- **Algorithm:** HS256
- **Expiration:** 8 hours (480 minutes)
- **Payload:**
  ```json
  {
    "email": "professor@sfsu.edu",
    "username": "johndoe",
    "id": 1,
    "exp": 1699999999
  }
  ```

### 3. **OTP Security**
- **Length:** 6 digits (100,000 - 999,999)
- **Expiration:** 10 minutes
- **Max Attempts:** 5 attempts per OTP
- **Single Use:** OTP deleted after successful verification

### 4. **Email Validation**
- Must end with `@sfsu.edu`
- Prevents non-SFSU users from registering

### 5. **Username Validation**
- 3-50 characters
- Must be unique
- No spaces allowed

### 6. **Protected Routes**
- All professor endpoints require valid JWT token
- Token validated using `verify_professor` dependency
- Automatic 401 response for invalid/expired tokens

---

## 🧪 Testing the System

### 1. **Manual Testing**

#### Test Registration:
```bash
# 1. Start backend
cd backend
python main.py

# 2. Start frontend
cd frontend
npm run dev

# 3. Navigate to http://localhost:5173/professor/register
# 4. Fill in the form:
#    - Name: Test Professor
#    - Username: testprof
#    - Email: test@sfsu.edu
#    - Department: Computer Science
# 5. Click "Send OTP"
# 6. Check console for dev OTP (if email not configured)
# 7. Enter OTP and click "Verify"
# 8. Set password and click "Create Account"
```

#### Test Login:
```bash
# 1. Navigate to http://localhost:5173/professor
# 2. Enter username: testprof
# 3. Enter password: your_password
# 4. Click "Login to Dashboard"
# 5. Should redirect to /professor/dashboard
```

### 2. **API Testing with cURL**

#### Test Login:
```bash
# Login with username
curl -X POST http://localhost:8000/professor/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Login with email
curl -X POST http://localhost:8000/professor/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin@sfsu.edu", "password": "admin123"}'
```

#### Test Protected Endpoint:
```bash
# Get corrections (requires auth)
curl http://localhost:8000/professor/corrections/pending \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 3. **Automated Test Script**

Create `test_auth.py`:
```python
import asyncio
import sys
sys.path.append('backend')

from backend.services.auth import AuthService
from backend.services.database import DatabaseService

async def test_auth():
    auth_service = AuthService()
    db_service = DatabaseService()

    print("1. Testing authentication with username...")
    prof = await auth_service.authenticate_professor("admin", "admin123")
    assert prof is not None, "Auth failed with username"
    print("✅ Username auth works")

    print("\n2. Testing authentication with email...")
    prof = await auth_service.authenticate_professor("admin@sfsu.edu", "admin123")
    assert prof is not None, "Auth failed with email"
    print("✅ Email auth works")

    print("\n3. Testing JWT token generation...")
    token = auth_service.create_access_token({"id": prof['id'], "email": prof['email']})
    assert token, "Token generation failed"
    print(f"✅ Token generated: {token[:20]}...")

    print("\n4. Testing token verification...")
    payload = auth_service.verify_token(token)
    assert payload is not None, "Token verification failed"
    print("✅ Token verified")

    print("\n✅ All authentication tests passed!")

if __name__ == "__main__":
    asyncio.run(test_auth())
```

Run:
```bash
python test_auth.py
```

---

## 📧 Email Configuration (Optional)

### Using Resend API

1. **Sign up for Resend:**
   - Go to https://resend.com
   - Create account and get API key

2. **Add to `.env`:**
```env
RESEND_API_KEY=re_xxxxxxxxxxxxx
SENDER_EMAIL=noreply@yourdomain.com
```

3. **Verify Domain:**
   - Add DNS records in Resend dashboard
   - Verify domain ownership

### Dev Mode (No Email Service)

If `RESEND_API_KEY` is not set:
- OTP printed to console
- OTP stored in memory
- Perfect for local development

---

## 🚀 Deployment Checklist

### Database:
- [ ] Run migration SQL to add username field
- [ ] Create test professor account
- [ ] Verify unique constraints on username and email

### Backend:
- [ ] Set `JWT_SECRET` to secure random string
- [ ] Configure `RESEND_API_KEY` for production emails
- [ ] Update CORS origins to production domain
- [ ] Test all auth endpoints

### Frontend:
- [ ] Update API base URL to production
- [ ] Test registration flow
- [ ] Test login flow
- [ ] Test token persistence

### Security:
- [ ] Change default `JWT_SECRET`
- [ ] Enable HTTPS only in production
- [ ] Set secure cookie flags
- [ ] Rate limit authentication endpoints

---

## 🐛 Troubleshooting

### "Email already registered"
**Solution:** User exists with that email. Use password reset or login.

### "Username already taken"
**Solution:** Choose a different username.

### "Invalid or expired OTP"
**Causes:**
- OTP expired (>10 minutes old)
- Too many attempts (>5)
- Wrong OTP entered

**Solution:** Click "Resend OTP"

### "Invalid username/email or password"
**Causes:**
- Wrong username or email
- Wrong password
- Account doesn't exist

**Solution:** Check credentials or register

### "Token expired" on dashboard
**Cause:** JWT token expired (8 hours)

**Solution:** Login again

### OTP not received
**Causes:**
- Email service not configured
- Wrong email address
- Email in spam folder

**Solution:**
- Check console for dev OTP
- Configure Resend API key
- Check spam folder

---

## 📝 Summary

### What You Now Have:

✅ **Username-based login** (can also use email)
✅ **OTP email verification** during registration
✅ **Secure password hashing** with bcrypt
✅ **JWT authentication** with 8-hour expiration
✅ **3-step registration** process
✅ **Protected professor** endpoints
✅ **Database schema** with username field
✅ **Frontend forms** for login and registration
✅ **Dev mode** for testing without email service

### Key Files:

**Backend:**
- `backend/services/auth.py` - Authentication logic
- `backend/services/email.py` - OTP email service
- `backend/main.py` - API endpoints

**Frontend:**
- `frontend/src/pages/ProfessorLogin.jsx` - Login page
- `frontend/src/pages/ProfessorRegister.jsx` - Registration page
- `frontend/src/services/api.js` - API client

**Database:**
- `database/add_username_to_professors.sql` - Migration script

---

**Questions or Issues?**
- Check troubleshooting section
- Review console logs for errors
- Test with demo credentials (username: admin, password: admin123)

---

**Last Updated:** October 11, 2025
**Version:** 2.0
