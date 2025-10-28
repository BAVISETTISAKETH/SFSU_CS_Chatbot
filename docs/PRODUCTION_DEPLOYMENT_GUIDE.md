# 🚀 Production Deployment Guide - SFSU CS Chatbot

**Status**: Ready for production deployment
**Estimated Time**: 30-60 minutes (depending on chosen method)
**Cost**: Free tier available for all services

---

## 📋 Pre-Deployment Checklist

Before deploying, ensure:

- [x] ✅ Session management implemented
- [x] ✅ Citations removed for production
- [x] ✅ Flag incorrect feature working
- [x] ✅ Notification system implemented
- [x] ✅ View correction details working
- [ ] ⚠️ SQL migrations run in Supabase
- [ ] ⚠️ Environment variables configured
- [ ] ⚠️ LLM provider chosen (Ollama vs Groq)

---

## 🎯 Quick Decision Guide

### Choose Your Deployment Path:

**Option A: Cloud Deployment with Groq (RECOMMENDED - Easiest)**
- ✅ No server management
- ✅ Free tier: 14,400 requests/day
- ✅ Deploy in 30 minutes
- ✅ Frontend: Vercel (Free)
- ✅ Backend: Railway/Render (Free tier)
- ✅ LLM: Groq API (Free)
- 📖 See Section 1 below

**Option B: VPS with Ollama (Advanced - More Control)**
- ⚠️ Requires VPS (DigitalOcean, AWS, etc.)
- ⚠️ Need to install Ollama + DeepSeek
- ⚠️ Higher cost ($5-20/month)
- ✅ No rate limits
- ✅ Full control
- 📖 See Section 2 below

**For most users**: Choose Option A (Groq)

---

## 🚀 SECTION 1: Cloud Deployment with Groq (RECOMMENDED)

### Overview:
- **Frontend**: Vercel (React + Vite)
- **Backend**: Railway or Render
- **Database**: Supabase (already set up)
- **LLM**: Groq API
- **Email**: Resend
- **Web Search**: SerpAPI

**Total Cost**: $0/month (free tiers)

---

### Step 1.1: Switch from Ollama to Groq

**Why**: Groq is free, cloud-based, and doesn't require server setup.

**File**: `backend/main.py`

**Change line 17**:
```python
# BEFORE:
from services.llm_ollama import OllamaLLMService as LLMService

# AFTER:
from services.llm_groq import GroqLLMService as LLMService
```

**Save the file** ✅

---

### Step 1.2: Verify Environment Variables

**File**: `backend/.env`

Make sure you have:
```env
# GROQ API (Free LLM) - GET KEY: https://console.groq.com/keys
GROQ_API_KEY=gsk_your_actual_groq_key_here

# SUPABASE (Already set up)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_DB_PASSWORD=your_db_password

# SERPAPI (Web Search) - GET KEY: https://serpapi.com/
SERPAPI_KEY=your_serpapi_key_here

# JWT SECRET (Generate random string)
JWT_SECRET=your_super_secret_random_string_here_minimum_32_chars

# EMAIL SERVICE - GET KEY: https://resend.com/api-keys
RESEND_API_KEY=re_your_resend_key_here
SENDER_EMAIL=noreply@yourdomain.com

# ENVIRONMENT
ENVIRONMENT=production
```

**How to get API keys**:
1. **Groq**: https://console.groq.com/keys (Free, instant)
2. **SerpAPI**: https://serpapi.com/users/sign_up (Free 100 searches/month)
3. **Resend**: https://resend.com/api-keys (Free 100 emails/day)
4. **JWT Secret**: Run `node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"`

---

### Step 1.3: Run SQL Migrations in Supabase

**Go to**: https://supabase.com/dashboard → Your Project → SQL Editor

**Run these SQL commands in order**:

#### 1. Add session_id to corrections table:
```sql
ALTER TABLE corrections
ADD COLUMN IF NOT EXISTS session_id VARCHAR(100);

CREATE INDEX IF NOT EXISTS corrections_session_id_idx ON corrections(session_id);
```

#### 2. Create notifications table:
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

**Click "Run"** for each ✅

---

### Step 1.4: Deploy Backend to Railway

**Why Railway**: Free $5 credit/month, easy deployment, automatic HTTPS

#### A. Create Railway Account
1. Go to https://railway.app/
2. Sign up with GitHub
3. Create new project → Deploy from GitHub repo

#### B. Connect Repository
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Authorize Railway to access your repo
4. Select `sfsu-cs-chatbot` repository

#### C. Configure Build Settings
1. **Root Directory**: `/backend`
2. **Build Command**: (leave empty)
3. **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

#### D. Add Environment Variables
In Railway dashboard, add these variables:
```
GROQ_API_KEY=your_groq_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
SUPABASE_DB_PASSWORD=your_db_password
SERPAPI_KEY=your_serpapi_key
JWT_SECRET=your_jwt_secret
RESEND_API_KEY=your_resend_key
SENDER_EMAIL=your_sender_email
ENVIRONMENT=production
PORT=8000
```

#### E. Deploy
1. Click "Deploy"
2. Wait for build to complete (2-3 minutes)
3. Railway will give you a URL like: `https://your-app.railway.app`
4. **Copy this URL** - you'll need it for frontend!

---

### Step 1.5: Deploy Frontend to Vercel

**Why Vercel**: Free, automatic HTTPS, optimized for React/Vite

#### A. Create Vercel Account
1. Go to https://vercel.com/
2. Sign up with GitHub

#### B. Deploy from GitHub
1. Click "Add New Project"
2. Import `sfsu-cs-chatbot` repository
3. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

#### C. Add Environment Variable
Click "Environment Variables" and add:
```
VITE_API_URL=https://your-app.railway.app
```
(Use the Railway URL from Step 1.4)

#### D. Deploy
1. Click "Deploy"
2. Wait 2-3 minutes
3. Vercel gives you a URL like: `https://your-app.vercel.app`
4. **This is your production chatbot!** 🎉

---

### Step 1.6: Update CORS in Backend

**File**: `backend/main.py` (lines 39-50)

Replace the CORS configuration:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-app.vercel.app",  # Your actual Vercel URL
        "https://*.vercel.app",          # Allow Vercel preview deployments
        "http://localhost:5173",         # Keep for local testing
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Commit and push** - Railway will auto-redeploy!

---

### Step 1.7: Test Production Deployment

1. **Visit your Vercel URL**: `https://your-app.vercel.app`
2. **Ask a question**: "What is CS 101?"
3. **Verify response**: Should get answer without [Local] tags
4. **Test flag incorrect**: Flag a response
5. **Login as professor**: Test dashboard
6. **Review flag**: Approve with correction
7. **Check notification**: Student should see notification bell

**If everything works** → ✅ You're LIVE!

---

## 🚀 SECTION 2: VPS Deployment with Ollama (Advanced)

### Overview:
- **Server**: DigitalOcean Droplet ($12/month) or AWS EC2
- **OS**: Ubuntu 22.04 LTS
- **LLM**: Ollama + DeepSeek R1 7B (local)
- **Frontend**: Nginx serving built React app
- **Backend**: Uvicorn with systemd

**Total Cost**: $12-20/month

---

### Step 2.1: Create VPS

#### Option A: DigitalOcean
1. Go to https://www.digitalocean.com/
2. Create Droplet
3. Choose:
   - **OS**: Ubuntu 22.04 LTS
   - **Plan**: Basic ($12/month)
   - **CPU**: 2 vCPU, 4GB RAM (minimum for Ollama)
   - **Storage**: 80GB SSD

#### Option B: AWS EC2
1. Launch EC2 instance
2. Choose `t3.medium` (2 vCPU, 4GB RAM)
3. Ubuntu 22.04 AMI

**Get your server IP**: e.g., `123.45.67.89`

---

### Step 2.2: Connect to Server

```bash
ssh root@your_server_ip
```

---

### Step 2.3: Install Dependencies

```bash
# Update system
apt update && apt upgrade -y

# Install Python 3.11
apt install python3.11 python3.11-venv python3-pip -y

# Install Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install nodejs -y

# Install Nginx
apt install nginx -y

# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull DeepSeek model (this takes 5-10 minutes)
ollama pull deepseek-r1:7b
```

---

### Step 2.4: Deploy Application

```bash
# Clone repository
cd /var/www
git clone https://github.com/yourusername/sfsu-cs-chatbot.git
cd sfsu-cs-chatbot

# Set up backend
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env file
nano .env
# (Paste your environment variables - see Step 1.2)
# Press Ctrl+X, Y, Enter to save

# Build frontend
cd ../frontend
npm install
npm run build
```

---

### Step 2.5: Configure Systemd Service

**Create backend service**:
```bash
nano /etc/systemd/system/sfsu-chatbot.service
```

**Paste**:
```ini
[Unit]
Description=SFSU Chatbot Backend
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/var/www/sfsu-cs-chatbot/backend
Environment="PATH=/var/www/sfsu-cs-chatbot/backend/venv/bin"
ExecStart=/var/www/sfsu-cs-chatbot/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

**Enable and start**:
```bash
systemctl daemon-reload
systemctl enable sfsu-chatbot
systemctl start sfsu-chatbot
systemctl status sfsu-chatbot
```

---

### Step 2.6: Configure Nginx

```bash
nano /etc/nginx/sites-available/sfsu-chatbot
```

**Paste**:
```nginx
server {
    listen 80;
    server_name your_domain.com;  # Or use IP address

    # Frontend
    location / {
        root /var/www/sfsu-cs-chatbot/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

**Enable site**:
```bash
ln -s /etc/nginx/sites-available/sfsu-chatbot /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

---

### Step 2.7: Set Up SSL (Optional but Recommended)

```bash
# Install Certbot
apt install certbot python3-certbot-nginx -y

# Get SSL certificate
certbot --nginx -d your_domain.com

# Auto-renewal is set up automatically
```

---

### Step 2.8: Update Frontend API URL

**File**: `frontend/.env` (rebuild after changing)

```env
VITE_API_URL=https://your_domain.com/api
```

**Rebuild frontend**:
```bash
cd /var/www/sfsu-cs-chatbot/frontend
npm run build
```

---

### Step 2.9: Test VPS Deployment

1. Visit `http://your_domain.com` or `http://your_server_ip`
2. Test all features (chat, flag, professor dashboard, notifications)
3. Check logs: `journalctl -u sfsu-chatbot -f`

---

## 🔒 Security Checklist

Before going live, ensure:

- [ ] All API keys in environment variables (NOT in code)
- [ ] JWT secret is strong (32+ random characters)
- [ ] CORS restricted to your domain only
- [ ] HTTPS enabled (SSL certificate)
- [ ] Supabase RLS (Row Level Security) enabled
- [ ] Rate limiting enabled
- [ ] Error messages don't expose sensitive info
- [ ] Database backups configured in Supabase

---

## 📊 Monitoring & Maintenance

### Option A (Cloud - Railway/Vercel):
- **Logs**: Check Railway dashboard and Vercel dashboard
- **Uptime**: Use https://uptimerobot.com/ (free monitoring)
- **Errors**: Built-in error tracking in dashboards

### Option B (VPS):
- **Logs**: `journalctl -u sfsu-chatbot -f`
- **Uptime**: Install monitoring (Prometheus + Grafana)
- **Server Health**: `htop`, `df -h`, `free -m`

---

## 💰 Cost Comparison

### Option A: Cloud (Groq)
- **Vercel**: Free (100GB bandwidth/month)
- **Railway**: Free $5 credit/month
- **Supabase**: Free (500MB database, 2GB bandwidth)
- **Groq**: Free (14,400 requests/day)
- **SerpAPI**: Free (100 searches/month)
- **Resend**: Free (100 emails/day)
- **Total**: $0/month (free tier) → $5-10/month if you exceed

### Option B: VPS (Ollama)
- **DigitalOcean**: $12/month
- **Domain**: $10-15/year
- **Supabase**: Free
- **Total**: $12-15/month

---

## 🐛 Troubleshooting

### Issue: Backend won't start
**Check**:
1. All environment variables set correctly
2. Python dependencies installed: `pip install -r requirements.txt`
3. Port 8000 not already in use: `lsof -i :8000`

### Issue: Frontend shows "Network Error"
**Check**:
1. Backend is running and accessible
2. VITE_API_URL is correct in frontend/.env
3. CORS allows your frontend domain

### Issue: "GROQ_API_KEY not found"
**Fix**: Set environment variable in Railway/Render dashboard or .env file

### Issue: Notifications not working
**Check**:
1. SQL migrations ran successfully (notifications table exists)
2. Session persistence enabled in frontend
3. Browser console for errors

### Issue: Ollama "Model not found"
**Fix**: Run `ollama pull deepseek-r1:7b` on server

---

## ✅ Final Checklist

Before announcing to users:

- [ ] Deployed to production (Option A or B)
- [ ] All SQL migrations run in Supabase
- [ ] Environment variables configured
- [ ] CORS configured correctly
- [ ] SSL/HTTPS enabled
- [ ] Tested full workflow:
  - [ ] Chat works
  - [ ] Responses don't have [Local] tags
  - [ ] Flag incorrect works
  - [ ] Professor can review flags
  - [ ] Notifications work
  - [ ] View correction details works
- [ ] Professor accounts created
- [ ] Monitoring set up
- [ ] Error tracking enabled
- [ ] Backups configured

---

## 🎉 You're Live!

**Next Steps**:
1. Create professor accounts using `add_admin.py`
2. Share URL with students
3. Monitor usage and feedback
4. Consider adding:
   - User login system
   - Email notifications
   - Analytics dashboard
   - Feedback system improvements

---

## 📞 Support

**Need Help?**
- Check logs first (Railway/Vercel dashboard or server logs)
- Verify environment variables
- Test locally to isolate issue
- Check Supabase dashboard for database issues

---

**Deployment Time**:
- Option A (Cloud/Groq): 30-45 minutes
- Option B (VPS/Ollama): 1-2 hours

**Recommended**: Start with Option A (easier), migrate to Option B later if needed.

**Go deploy!** 🚀
