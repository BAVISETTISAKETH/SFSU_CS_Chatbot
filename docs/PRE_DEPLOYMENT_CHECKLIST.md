# ✅ Pre-Deployment Checklist

**Before deploying to production, verify everything works locally!**

---

## 📋 Code Changes Completed

- [x] ✅ Switched from Ollama to Groq (`backend/main.py:17`)
- [x] ✅ Session persistence enabled (for notifications)
- [x] ✅ Citations removed from responses
- [x] ✅ Flag incorrect feature implemented
- [x] ✅ Notification system implemented
- [x] ✅ View correction details implemented

---

## 🔑 Environment Variables Checklist

### Backend (.env file)

Check `backend/.env` has all these:

- [ ] `GROQ_API_KEY` - Get from https://console.groq.com/keys
- [ ] `SUPABASE_URL` - From Supabase dashboard
- [ ] `SUPABASE_KEY` - Anon key from Supabase
- [ ] `SUPABASE_DB_PASSWORD` - Your database password
- [ ] `SERPAPI_KEY` - Get from https://serpapi.com/ (free 100/month)
- [ ] `JWT_SECRET` - Random 32+ character string
- [ ] `RESEND_API_KEY` - Get from https://resend.com/ (free 100 emails/day)
- [ ] `SENDER_EMAIL` - Your sender email
- [ ] `ENVIRONMENT=production`

### Frontend (.env file)

Check `frontend/.env` has:

- [ ] `VITE_API_URL=http://localhost:8000` (for local testing)
  - **Will change to Railway URL after deployment**

---

## 🗄️ Database Migrations

### 1. Add session_id to corrections table

```sql
ALTER TABLE corrections
ADD COLUMN IF NOT EXISTS session_id VARCHAR(100);

CREATE INDEX IF NOT EXISTS corrections_session_id_idx ON corrections(session_id);
```

**Status**: [ ] Not run / [x] Completed

### 2. Create notifications table

```sql
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

CREATE INDEX IF NOT EXISTS notifications_session_id_idx ON notifications(session_id);
CREATE INDEX IF NOT EXISTS notifications_is_read_idx ON notifications(is_read);
CREATE INDEX IF NOT EXISTS notifications_created_at_idx ON notifications(created_at DESC);
```

**Status**: [ ] Not run / [x] Completed

---

## 🧪 Local Testing (CRITICAL - Do This Before Deploying!)

### Step 1: Test Backend with Groq

```bash
cd D:\sfsu-cs-chatbot\backend
..\venv\Scripts\python.exe main.py
```

**Expected**:
- ✅ Server starts without errors
- ✅ No "GROQ_API_KEY not found" error
- ✅ See: "Application startup complete"

**Status**: [ ] Not tested / [x] Passed

---

### Step 2: Test Frontend

```bash
cd D:\sfsu-cs-chatbot\frontend
npm run dev
```

**Expected**:
- ✅ Vite dev server starts
- ✅ No build errors
- ✅ See: "Local: http://localhost:5173"

**Status**: [ ] Not tested / [x] Passed

---

### Step 3: Test Chat Functionality

**Open**: http://localhost:5173

1. **Ask a question**: "What is CS 101?"
   - [ ] ✅ Gets response
   - [ ] ✅ Response is relevant
   - [ ] ✅ NO `[Local]` or `[Web]` tags visible
   - [ ] ✅ Response is clean and readable

2. **Flag incorrect**:
   - [ ] ✅ "Flag as incorrect" button appears
   - [ ] ✅ Can click and enter reason
   - [ ] ✅ Submit works (no error)
   - [ ] ✅ Success message appears

3. **Professor Dashboard**:
   - [ ] ✅ Can access dashboard
   - [ ] ✅ Flagged item appears in "Pending Corrections"
   - [ ] ✅ Can review flag (approve/reject/edit)
   - [ ] ✅ Submit works without error

4. **Notifications**:
   - [ ] ✅ Student sees notification bell badge
   - [ ] ✅ Click bell shows notification
   - [ ] ✅ "View Response" button appears
   - [ ] ✅ Modal opens showing correction details
   - [ ] ✅ Modal shows original vs corrected response

---

## 🔒 Security Checklist

Before deploying:

- [ ] JWT_SECRET is strong (32+ random characters)
- [ ] No API keys in code (all in .env)
- [ ] .env files in .gitignore
- [ ] CORS will be configured for production domain
- [ ] Supabase RLS (Row Level Security) enabled
- [ ] No sensitive data logged
- [ ] Error messages don't expose system details

---

## 📦 Build Test (Optional but Recommended)

### Test Production Build Locally

```bash
# Build frontend
cd D:\sfsu-cs-chatbot\frontend
npm run build

# Preview production build
npm run preview
```

**Expected**:
- [ ] ✅ Build completes without errors
- [ ] ✅ Preview server starts
- [ ] ✅ App works the same as dev mode

---

## 🚀 Ready for Deployment?

If all above checks pass:

- [x] ✅ Code changes complete
- [ ] ✅ Environment variables configured
- [ ] ✅ Database migrations run
- [ ] ✅ Local testing passed (all features work)
- [ ] ✅ Security checks passed
- [ ] ✅ Build test passed (optional)

**If ALL checked** → ✅ **Ready to deploy!**

**If ANY unchecked** → ⚠️ **Fix issues before deploying**

---

## 📝 Deployment Accounts Needed

Make sure you have accounts on:

- [ ] **GitHub** - For repository hosting
- [ ] **Railway** or **Render** - For backend hosting
- [ ] **Vercel** or **Netlify** - For frontend hosting
- [ ] **Supabase** - Already have (database)
- [ ] **Groq** - For LLM API (free)
- [ ] **SerpAPI** - For web search (free tier)
- [ ] **Resend** - For emails (free tier)

---

## 🎯 Next Steps

1. **If local testing passes**: Follow `DEPLOY_NOW.md`
2. **If issues found**: Fix them, re-test, then deploy
3. **After deployment**: Test production URLs thoroughly

---

## 🐛 Common Pre-Deployment Issues

### Issue: Backend won't start
**Check**:
- [ ] GROQ_API_KEY is set in backend/.env
- [ ] All required packages installed: `pip install -r requirements.txt`
- [ ] Python version 3.11+ installed

### Issue: "Network Error" in frontend
**Check**:
- [ ] Backend is running on port 8000
- [ ] VITE_API_URL is set to http://localhost:8000
- [ ] No firewall blocking port 8000

### Issue: Chat gives no response
**Check**:
- [ ] GROQ_API_KEY is valid
- [ ] Internet connection working
- [ ] Check backend terminal for errors

### Issue: Flag incorrect doesn't work
**Check**:
- [ ] SQL migration 1 ran successfully (session_id column exists)
- [ ] Check browser console for errors
- [ ] Check backend logs for database errors

### Issue: Notifications don't show
**Check**:
- [ ] SQL migration 2 ran successfully (notifications table exists)
- [ ] Session persistence enabled in frontend
- [ ] Check browser console for errors

---

## ✅ Sign-Off

Before deploying to production, I certify that:

- [ ] All code changes are complete and tested
- [ ] All environment variables are configured
- [ ] All database migrations have been run
- [ ] All local tests pass
- [ ] I have Groq API key and it works
- [ ] I understand the deployment process
- [ ] I have backup of database (Supabase auto-backups enabled)

**Signed**: _______________ **Date**: _______________

---

**Once all boxes are checked, proceed to `DEPLOY_NOW.md`!** 🚀
