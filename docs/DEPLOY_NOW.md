# 🚀 Deploy to Production NOW - Quick Start

**Time**: 30 minutes
**Cost**: FREE (using free tiers)
**Difficulty**: Easy

---

## ✅ Pre-Flight Checklist

Before you start, make sure you have:

- [ ] GitHub account
- [ ] Supabase account (you already have this)
- [ ] All your environment variables ready (.env files)

---

## 🎯 Step 1: Switch to Groq (Production LLM)

**Why**: Ollama requires a server to run locally. Groq is cloud-based and FREE!

### Change 1 Line of Code:

**File**: `backend/main.py` (Line 17)

**BEFORE**:
```python
from services.llm_ollama import OllamaLLMService as LLMService
```

**AFTER**:
```python
from services.llm import LLMService
```

**Save the file** ✅

---

## 🔑 Step 2: Get Groq API Key (2 minutes)

1. Go to https://console.groq.com/keys
2. Sign up with Google/GitHub
3. Click "Create API Key"
4. Copy the key (starts with `gsk_...`)

**Add to** `backend/.env`:
```env
GROQ_API_KEY=gsk_your_actual_key_here
```

---

## 🗄️ Step 3: Run SQL Migrations in Supabase (2 minutes)

1. Go to https://supabase.com/dashboard
2. Open your project
3. Click **SQL Editor** → **New query**
4. Copy and paste:

```sql
-- 1. Add session_id to corrections table
ALTER TABLE corrections
ADD COLUMN IF NOT EXISTS session_id VARCHAR(100);

CREATE INDEX IF NOT EXISTS corrections_session_id_idx ON corrections(session_id);

-- 2. Create notifications table
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

5. Click **Run** ✅

---

## 🚂 Step 4: Deploy Backend to Railway (10 minutes)

### A. Create Railway Account
1. Go to https://railway.app/
2. Click "Login" → Sign in with GitHub
3. Authorize Railway

### B. Create New Project
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose your `sfsu-cs-chatbot` repository
4. If you don't see it, click "Configure GitHub App" and grant access

### C. Configure Service
1. Railway will detect your app - Click "Add variables"
2. Click "Raw Editor" and paste:

```
GROQ_API_KEY=your_groq_key_here
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_DB_PASSWORD=your_db_password
SERPAPI_KEY=your_serpapi_key
JWT_SECRET=your_jwt_secret_minimum_32_chars
RESEND_API_KEY=your_resend_key
SENDER_EMAIL=noreply@yourdomain.com
ENVIRONMENT=production
PORT=8000
```

3. Replace with your actual values!

### D. Configure Build
1. Click "Settings" tab
2. **Root Directory**: Change to `backend`
3. **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Click "Deploy"

### E. Get Your Backend URL
1. Wait for deployment (2-3 minutes)
2. Click "Settings" → "Networking" → "Generate Domain"
3. You'll get a URL like: `https://sfsu-chatbot-production.up.railway.app`
4. **COPY THIS URL** - you need it for frontend!

---

## 🎨 Step 5: Deploy Frontend to Vercel (10 minutes)

### A. Create Vercel Account
1. Go to https://vercel.com/
2. Sign up with GitHub
3. Authorize Vercel

### B. Import Project
1. Click "Add New..." → "Project"
2. Find and import `sfsu-cs-chatbot` repository
3. Configure project:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

### C. Add Environment Variable
1. Click "Environment Variables"
2. Add:
   - **Name**: `VITE_API_URL`
   - **Value**: `https://your-railway-url.up.railway.app` (from Step 4E)
3. Click "Add"

### D. Deploy
1. Click "Deploy"
2. Wait 2-3 minutes
3. Vercel gives you a URL like: `https://sfsu-chatbot.vercel.app`
4. **THIS IS YOUR PRODUCTION CHATBOT!** 🎉

---

## 🔧 Step 6: Update CORS (5 minutes)

**File**: `backend/main.py` (lines 39-50)

**Change**:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-app.vercel.app",  # Replace with YOUR Vercel URL
        "https://*.vercel.app",          # For Vercel preview deployments
        "http://localhost:5173",         # Keep for local testing
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Save, commit, and push**:
```bash
git add .
git commit -m "Configure CORS for production"
git push
```

Railway will auto-redeploy! (takes 2 minutes)

---

## 🧪 Step 7: Test Your Production App

1. Visit your Vercel URL: `https://your-app.vercel.app`
2. Ask: "What is CS 101?"
3. Verify you get a response
4. Test flag incorrect feature
5. Login as professor (you'll need to create professor account first)

---

## 👨‍🏫 Step 8: Create Professor Account (Optional)

**On your local machine**:
```bash
cd D:\sfsu-cs-chatbot
venv\Scripts\python.exe add_admin.py
```

Follow prompts to create professor account.

---

## ✅ Success Checklist

Your app is live when:

- [ ] Vercel URL loads the chatbot interface
- [ ] You can ask questions and get responses
- [ ] Responses don't have [Local] or [Web] tags
- [ ] Flag incorrect button works
- [ ] Professor dashboard loads
- [ ] Notifications work

---

## 🐛 Common Issues

### Issue 1: "Network Error" in chat
**Fix**: Check backend logs in Railway dashboard, verify VITE_API_URL is correct

### Issue 2: "GROQ_API_KEY not found"
**Fix**: Add the API key in Railway environment variables, then redeploy

### Issue 3: CORS error in browser console
**Fix**: Update CORS allow_origins in backend/main.py with your actual Vercel URL

### Issue 4: Frontend shows blank page
**Fix**: Check Vercel build logs, verify VITE_API_URL environment variable is set

---

## 💰 Costs (All FREE for small usage)

- **Vercel**: Free (100GB bandwidth/month)
- **Railway**: Free $5 credit/month (usually enough for small apps)
- **Groq**: Free (14,400 requests/day = ~10 requests/minute)
- **Supabase**: Free (500MB database)
- **SerpAPI**: Free (100 searches/month)
- **Resend**: Free (100 emails/day)

**Total**: $0/month unless you get lots of traffic!

---

## 📊 Monitor Your App

### Railway (Backend):
- Dashboard: https://railway.app/
- View logs, metrics, and errors
- Monitor usage and costs

### Vercel (Frontend):
- Dashboard: https://vercel.com/dashboard
- View deployments and analytics
- Check build logs

### Supabase (Database):
- Dashboard: https://supabase.com/dashboard
- Monitor database size and queries
- Set up database backups

---

## 🎉 You're LIVE!

**What you just built**:
- ✅ AI chatbot for SFSU students
- ✅ RAG with local + web search
- ✅ Flag incorrect responses
- ✅ Professor correction workflow
- ✅ Real-time notifications
- ✅ Production-ready infrastructure

**Share your app**:
- Give students the Vercel URL
- Create professor accounts
- Monitor feedback and usage

**Next steps**:
- Add custom domain (Vercel settings)
- Set up monitoring (UptimeRobot)
- Add analytics (Google Analytics)
- Collect user feedback

---

## 📁 Files You Modified

1. `backend/main.py` - Switched to Groq, updated CORS
2. Supabase database - Ran SQL migrations
3. Railway - Configured environment variables
4. Vercel - Configured build settings

---

## 🚀 Quick Command Reference

```bash
# Test locally before deploying
cd D:\sfsu-cs-chatbot\backend
..\venv\Scripts\python.exe main.py

cd D:\sfsu-cs-chatbot\frontend
npm run dev

# Commit changes
git add .
git commit -m "Production ready"
git push

# Check Railway logs
# Go to Railway dashboard → Your project → View logs

# Check Vercel logs
# Go to Vercel dashboard → Your project → View logs
```

---

## ⏱️ Total Time Breakdown

- Step 1 (Switch to Groq): 1 minute
- Step 2 (Get API key): 2 minutes
- Step 3 (SQL migrations): 2 minutes
- Step 4 (Deploy backend): 10 minutes
- Step 5 (Deploy frontend): 10 minutes
- Step 6 (Update CORS): 5 minutes
- Step 7 (Testing): 5 minutes

**Total**: ~35 minutes

---

## 🆘 Need Help?

1. **Check logs first**:
   - Railway: Backend logs
   - Vercel: Frontend build logs
   - Browser: F12 → Console for frontend errors

2. **Common fixes**:
   - Redeploy on Railway/Vercel
   - Clear browser cache
   - Verify environment variables
   - Check CORS settings

3. **Still stuck?**
   - Check Railway/Vercel documentation
   - Verify all environment variables are set correctly
   - Test locally first to isolate the issue

---

**Ready to deploy?** Start with Step 1! 🚀

**Questions?** Check the full guide: `PRODUCTION_DEPLOYMENT_GUIDE.md`
