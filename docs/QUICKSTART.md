# ⚡ QUICK START - Get Running in 10 Minutes!

You have all the code ready. Follow these steps to get your chatbot running locally:

---

## 🎯 STEP 1: Setup Database (3 minutes)

### 1.1 Open Supabase SQL Editor

1. Go to: https://supabase.com/dashboard
2. Select project: `sfsu-cs-chatbot`
3. Click **"SQL Editor"** (left sidebar)
4. Click **"New Query"**

### 1.2 Run Schema

1. Open file: `D:\sfsu-cs-chatbot\database\schema.sql`
2. Copy **ALL** contents (Ctrl+A, Ctrl+C)
3. Paste into Supabase SQL Editor
4. Click **"RUN"** (or Ctrl+Enter)
5. ✅ Should see "Success. No rows returned"

### 1.3 Verify

- Click "Table Editor" (left sidebar)
- You should see 6 tables: documents, verified_facts, corrections, professors, chat_logs, web_search_cache
- ✅ Database ready!

---

## 🎯 STEP 2: Install Backend Dependencies (2 minutes)

```bash
# Open terminal in D:\sfsu-cs-chatbot

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## 🎯 STEP 3: Migrate Your Data (5 minutes)

```bash
# Run migration script
python database\migrate_data.py
```

**What happens:**
- Reads all your JSON files from `data/` folder
- Generates vector embeddings
- Uploads to Supabase cloud database
- Takes ~5-10 min depending on data size

**Expected output:**
```
🔄 Loading embedding model...
✅ Loaded all-MiniLM-L6-v2 (384 dimensions)
🔌 Testing Supabase connection...
✅ Connected! Current document count: 0
📂 Found X JSON files...
...
🎉 Migration Complete!
```

---

## 🎯 STEP 4: Start Backend (30 seconds)

```bash
# Navigate to backend folder
cd backend

# Run the server
python main.py
```

**Expected output:**
```
🚀 Starting SFSU CS Chatbot API...
✅ Groq LLM: True
✅ RAG Service: True
✅ Web Search: True
✅ Database: True
🎉 All services ready!
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Test it:**
- Open browser: http://localhost:8000
- Should see JSON response with "status": "online"

---

## 🎯 STEP 5: Install & Start Frontend (2 minutes)

**Open a NEW terminal** (keep backend running in the other one)

```bash
# Navigate to frontend
cd D:\sfsu-cs-chatbot\frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

**Expected output:**
```
VITE v5.x.x  ready in 500 ms

  ➜  Local:   http://localhost:5173/
```

---

## 🎯 STEP 6: Test Everything! (1 minute)

### Test Student Chat

1. Open: http://localhost:5173
2. Type: "What courses does CS offer?"
3. ✅ Should get a response!

### Test Professor Login

1. Click "Professor Login" link (top right)
2. Login:
   - Email: `admin@sfsu.edu`
   - Password: `admin123`
3. ✅ Should see professor dashboard!

---

## 🎉 SUCCESS!

If everything above worked, you have:

- ✅ Cloud database (Supabase) with your data
- ✅ Backend API running (Groq LLM + RAG + Web Search)
- ✅ Frontend chat interface
- ✅ Professor dashboard with correction workflow

---

## ⚠️ TROUBLESHOOTING

### Backend won't start?

**Error: "GROQ_API_KEY not found"**
- Check `.env` file exists in root folder (`D:\sfsu-cs-chatbot\.env`)
- Verify it has: `GROQ_API_KEY=gsk_...`

**Error: Database connection failed**
- Go to Supabase dashboard
- Check project is active (not paused)
- Verify you ran schema.sql

### Frontend shows errors?

**Error: "Failed to fetch" or CORS**
- Make sure backend is running on http://localhost:8000
- Check backend terminal for errors

**Dependencies won't install?**
```bash
# Try:
npm install --legacy-peer-deps
```

### Migration script errors?

**"No JSON files found"**
- Check `data/` folder has .json files
- Run: `dir data` to verify

**"Failed to upload batch"**
- Database schema might not be created
- Re-run `schema.sql` in Supabase

---

## 📊 QUICK TEST CHECKLIST

- [ ] Supabase dashboard shows 6 tables created
- [ ] Backend starts without errors (port 8000)
- [ ] Can access http://localhost:8000 in browser
- [ ] Frontend starts (port 5173)
- [ ] Can send chat messages and get responses
- [ ] Professor login works (admin@sfsu.edu / admin123)

**All checked? You're ready to use and deploy! 🚀**

---

## 🔗 NEXT STEPS

1. **Test the correction workflow:**
   - Ask a question as student
   - Click "Flag Incorrect"
   - Login as professor
   - Review and approve/correct/reject

2. **Add more professors:**
   - Go to Supabase > Table Editor > professors
   - Add new rows with hashed passwords

3. **Deploy to production:**
   - See `DEPLOYMENT.md` for Railway + Vercel deployment

---

## 🆘 STILL STUCK?

**Common issues:**

| Symptom | Fix |
|---------|-----|
| "Module not found" | Run `pip install -r requirements.txt` |
| Port 8000 in use | Kill other process: `taskkill /F /IM python.exe` |
| No chat responses | Check backend logs, verify data migrated |
| Professor login fails | Password is `admin123` (no spaces) |

**Everything working?** Congratulations! You have a production-ready chatbot! 🎊
