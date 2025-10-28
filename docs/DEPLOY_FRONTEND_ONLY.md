# 🚀 Deploy Frontend Only - For Demo/Review

**Use Case**: Share a public link with professors while keeping backend + Ollama on your local machine

**Cost**: FREE
**Time**: 15-30 minutes
**Perfect for**: Testing, demos, reviews

---

## 🎯 Architecture

```
Your Local Machine:
├── Backend (localhost:8000) ✅ Running Ollama
├── Ollama + DeepSeek R1 ✅ Working locally
└── Exposed via Cloudflare Tunnel → Public URL

Cloud (FREE):
└── Frontend (Vercel/Netlify) → Public URL
    └── Connects to your local backend via tunnel
```

---

## ✅ What You Get

- ✅ Public link to share (e.g., `https://sfsu-chatbot.vercel.app`)
- ✅ Professors can access from anywhere
- ✅ Backend + Ollama stay on your machine (no server costs!)
- ✅ Completely FREE
- ✅ No rate limits (using your local Ollama)

---

## 🚀 Two Methods

### Method 1: Cloudflare Tunnel (RECOMMENDED - FREE Forever)
- ✅ Free forever
- ✅ Stable URL
- ✅ No bandwidth limits
- ✅ HTTPS included
- Time: 20 minutes

### Method 2: ngrok (Easier but Limited)
- ✅ Free tier available
- ⚠️ URL changes every restart
- ⚠️ 40 requests/minute limit (free tier)
- Time: 10 minutes

---

## 🚀 METHOD 1: Cloudflare Tunnel (RECOMMENDED)

### Step 1: Install Cloudflare Tunnel

**Windows**:
1. Download: https://github.com/cloudflare/cloudflared/releases/latest
2. Download `cloudflared-windows-amd64.exe`
3. Rename to `cloudflared.exe`
4. Move to `C:\Windows\System32\` (or any folder in PATH)

**Or install via command**:
```bash
# Download installer
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe -o cloudflared.exe

# Move to accessible location
move cloudflared.exe C:\Windows\System32\
```

**Verify installation**:
```bash
cloudflared --version
```

---

### Step 2: Start Your Backend Locally

```bash
cd D:\sfsu-cs-chatbot\backend
..\venv\Scripts\python.exe main.py
```

**Make sure**:
- ✅ Backend running on `http://localhost:8000`
- ✅ Ollama running (you can test the chatbot locally)
- ✅ No errors in terminal

**Keep this terminal open!**

---

### Step 3: Create Cloudflare Tunnel

**Open NEW terminal** and run:

```bash
cloudflared tunnel --url http://localhost:8000
```

**You'll see output like**:
```
2025-01-27 Your quick tunnel has been created! Visit:
  https://random-words-1234.trycloudflare.com
```

**Copy this URL!** This is your public backend URL.

Example: `https://random-words-1234.trycloudflare.com`

---

### Step 4: Update Frontend Environment

**Edit** `frontend/.env`:

```env
VITE_API_URL=https://random-words-1234.trycloudflare.com
```

**Replace with YOUR actual Cloudflare URL from Step 3**

---

### Step 5: Update Backend CORS

**Edit** `backend/main.py` (lines 39-50):

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",           # Local development
        "https://*.vercel.app",             # Vercel deployment
        "https://*.netlify.app",            # Netlify deployment
        "*"  # Allow all (for testing - restrict in production)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Save and restart backend**:
```bash
# Press Ctrl+C in backend terminal
# Then restart:
..\venv\Scripts\python.exe main.py
```

---

### Step 6: Deploy Frontend to Vercel

#### A. Create Vercel Account
1. Go to https://vercel.com
2. Sign up with GitHub
3. Authorize Vercel

#### B. Push Code to GitHub (if not already)

```bash
cd D:\sfsu-cs-chatbot

# Initialize git (if not done)
git init

# Add all files
git add .

# Commit
git commit -m "Ready for frontend deployment"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/sfsu-cs-chatbot.git
git branch -M main
git push -u origin main
```

#### C. Import to Vercel

1. Click "Add New..." → "Project"
2. Import your `sfsu-cs-chatbot` repository
3. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

4. **Environment Variables**:
   - Click "Environment Variables"
   - Add variable:
     - **Name**: `VITE_API_URL`
     - **Value**: `https://random-words-1234.trycloudflare.com` (your Cloudflare URL)

5. Click "Deploy"

**Wait 2-3 minutes...**

You'll get a URL like: `https://sfsu-chatbot.vercel.app`

---

### Step 7: Test Your Deployed Site

1. Visit your Vercel URL: `https://sfsu-chatbot.vercel.app`
2. Ask a question: "What is CS 101?"
3. Should get response from your local Ollama!

**If it works** → ✅ You're done! Share the Vercel URL!

---

### Step 8: Keep Everything Running

**To keep the demo running**, you need 3 terminals open:

**Terminal 1 - Backend**:
```bash
cd D:\sfsu-cs-chatbot\backend
..\venv\Scripts\python.exe main.py
```

**Terminal 2 - Cloudflare Tunnel**:
```bash
cloudflared tunnel --url http://localhost:8000
```

**Terminal 3 - (Optional) Test locally**:
```bash
cd D:\sfsu-cs-chatbot\frontend
npm run dev
```

**Now**:
- ✅ Professors can access: `https://sfsu-chatbot.vercel.app`
- ✅ Your local backend + Ollama handles all requests
- ✅ Completely FREE!

---

## 🚀 METHOD 2: ngrok (Quicker but Limited)

### Step 1: Install ngrok

1. Go to https://ngrok.com/
2. Sign up (free)
3. Download ngrok for Windows
4. Extract to a folder

### Step 2: Get Auth Token

1. Go to https://dashboard.ngrok.com/get-started/your-authtoken
2. Copy your auth token
3. Run:
```bash
ngrok config add-authtoken YOUR_TOKEN_HERE
```

### Step 3: Start Backend

```bash
cd D:\sfsu-cs-chatbot\backend
..\venv\Scripts\python.exe main.py
```

### Step 4: Start ngrok Tunnel

**In new terminal**:
```bash
ngrok http 8000
```

**You'll see**:
```
Forwarding    https://abc123.ngrok-free.app -> http://localhost:8000
```

**Copy the HTTPS URL**: `https://abc123.ngrok-free.app`

### Step 5: Update Frontend & Deploy

Same as Method 1, Steps 4-7, but use your ngrok URL instead.

**⚠️ Limitations of ngrok free tier**:
- URL changes every time you restart ngrok
- 40 requests/minute limit
- Session expires after 2 hours

---

## 💰 Cost Comparison

| Method | Cost | Pros | Cons |
|--------|------|------|------|
| **Cloudflare Tunnel** | FREE | Stable, unlimited | None! |
| **ngrok** | FREE | Easy | URL changes, 40 req/min |
| **Deploy Backend** | $12/month | 24/7 uptime | Costs money |

---

## 📋 Quick Summary

### What You Did:
1. ✅ Backend + Ollama running on your computer
2. ✅ Cloudflare Tunnel exposes backend to internet
3. ✅ Frontend deployed to Vercel (free)
4. ✅ Professors can access via public URL

### What It Costs:
- **Vercel**: FREE
- **Cloudflare Tunnel**: FREE
- **Backend**: Running on your machine (free)
- **Total**: **$0**

### Limitations:
- ⚠️ Your computer must be on and running
- ⚠️ If you close laptop or shut down, site stops working
- ⚠️ Good for: Demos, reviews, testing
- ⚠️ NOT good for: 24/7 production use

---

## 🎯 For Long-Term Production

If you want 24/7 uptime without your computer running:

**Then you need to deploy backend to a server** → Follow `DEPLOY_WITH_OLLAMA.md` ($12/month)

---

## 🐛 Troubleshooting

### Issue: "Network Error" on Vercel site
**Check**:
1. Backend is running locally
2. Cloudflare tunnel is running
3. VITE_API_URL in Vercel matches Cloudflare URL
4. CORS allows your Vercel domain

### Issue: Cloudflare tunnel URL not working
**Fix**:
- Make sure backend is running FIRST
- Then start Cloudflare tunnel
- Copy the EXACT URL (with https://)

### Issue: Vercel build fails
**Check**:
- Root directory is set to `frontend`
- Build command is `npm run build`
- Output directory is `dist`

---

## ✅ Final Steps

1. **Share your Vercel URL** with professors:
   ```
   https://sfsu-chatbot.vercel.app
   ```

2. **Keep these running**:
   - Backend (Terminal 1)
   - Cloudflare Tunnel (Terminal 2)

3. **When done for the day**:
   - Ctrl+C in both terminals to stop
   - Next time: Restart backend + tunnel (URL might change with tunnel)

---

## 🔄 Update Vercel if Tunnel URL Changes

If you restart Cloudflare Tunnel and get a new URL:

1. Go to https://vercel.com/dashboard
2. Select your project
3. Go to "Settings" → "Environment Variables"
4. Update `VITE_API_URL` with new Cloudflare URL
5. Go to "Deployments" tab
6. Click "..." on latest deployment → "Redeploy"

**Takes 2 minutes to update!**

---

## ⏱️ Time Breakdown

- Install Cloudflare Tunnel: 5 min
- Start backend + tunnel: 2 min
- Deploy frontend to Vercel: 10 min
- Test: 3 min
- **Total**: ~20 minutes

---

## 🎉 You're Done!

**What professors see**:
- Professional public URL
- Full working chatbot
- All features working (flag, notifications, etc.)

**What you have**:
- Backend + Ollama on your machine
- $0 cost
- Easy to stop/start

**Perfect for demos and reviews!** ✅

---

**Ready to deploy?** Follow the steps above and you'll have a shareable link in 20 minutes! 🚀
