# 🚀 SFSU CS Chatbot - Setup Guide

## 📋 Prerequisites

- [x] All API accounts created (Groq, Supabase, SerpAPI, Railway, Vercel)
- [x] `.env` file configured with your API keys
- [x] Python 3.9+ installed
- [x] Node.js 18+ installed
- [x] Git installed

---

## STEP 1: Database Setup (Supabase)

### 1.1 Run Database Schema

1. **Go to Supabase Dashboard**: https://supabase.com/dashboard

2. **Select your project**: `sfsu-cs-chatbot`

3. **Open SQL Editor**:
   - Click "SQL Editor" in left sidebar
   - Click "New Query"

4. **Copy & Paste**:
   - Open `database/schema.sql` in your code editor
   - Copy ALL the contents
   - Paste into Supabase SQL Editor

5. **Run the script**:
   - Click "RUN" button (or press `Ctrl+Enter`)
   - ✅ You should see "Success. No rows returned"

6. **Verify tables created**:
   - Click "Table Editor" in left sidebar
   - You should see these tables:
     - `documents`
     - `verified_facts`
     - `corrections`
     - `professors`
     - `chat_logs`
     - `web_search_cache`

7. **Check default professor account**:
   - Click on `professors` table
   - You should see 1 row: `admin@sfsu.edu`
   - Default password: `admin123` (⚠️ CHANGE THIS LATER!)

---

## STEP 2: Install Python Dependencies

```bash
# Create virtual environment (if not exists)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## STEP 3: Migrate Your Data to Supabase

This will upload all your JSON data to the cloud database with vector embeddings.

```bash
# Run migration script
python database/migrate_data.py
```

**What to expect:**
- ⏳ Takes ~5-10 minutes depending on data size
- ✅ Will skip very large files (>100MB) automatically
- 📊 Shows progress for each file
- ☁️  Uploads to Supabase with embeddings

**If you see errors:**
- Make sure database schema is created (Step 1)
- Check `.env` file has correct credentials
- Verify Supabase project is active

---

## STEP 4: Test the Backend API

```bash
# Navigate to backend directory
cd backend

# Run the FastAPI server
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

**Test in browser:**
- Open: http://localhost:8000
- You should see:
```json
{
  "status": "online",
  "service": "SFSU CS Chatbot API",
  "version": "2.0.0",
  "features": ["RAG", "Web Search", "Professor Corrections"]
}
```

**Test the chat endpoint:**
```bash
# Open a new terminal and run:
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"What is the CS department?\"}"
```

---

## STEP 5: Setup Frontend

```bash
# Navigate to frontend directory (from root)
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

**Expected output:**
```
VITE v5.x.x  ready in 500 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

**Open in browser:**
- Go to: http://localhost:5173
- You should see the chatbot interface!

---

## STEP 6: Test End-to-End

### 6.1 Test Student Chat

1. Open frontend: http://localhost:5173
2. Type a question: "What courses does SFSU CS offer?"
3. ✅ Should get a response from RAG

### 6.2 Test Professor Login

1. Click "Professor Login" (or navigate to `/professor`)
2. Login with:
   - Email: `admin@sfsu.edu`
   - Password: `admin123`
3. ✅ Should see professor dashboard

### 6.3 Test Correction Workflow

1. As student: Ask a question
2. Click "Flag Incorrect" if you want to test
3. Login as professor
4. See the flagged response in "Pending Corrections"
5. Approve/Correct/Reject it
6. ✅ Workflow complete!

---

## 🐛 Troubleshooting

### Backend won't start

**Error: "GROQ_API_KEY not found"**
- Check `.env` file exists in root directory
- Verify `GROQ_API_KEY=gsk_...` is set

**Error: "SUPABASE_URL and SUPABASE_KEY must be set"**
- Check `.env` file has both values
- No quotes needed around values

**Error: Database connection failed**
- Go to Supabase dashboard
- Check project is active (not paused)
- Verify database schema is created

### Frontend won't connect to backend

**Error: "Failed to fetch" or CORS error**
- Make sure backend is running on port 8000
- Check backend terminal for errors
- Verify `.env.local` in frontend has correct API URL

### Migration script errors

**Error: "No JSON files found"**
- Check `data/` folder has .json files
- Try: `ls data/`

**Error: "Failed to upload batch"**
- Database schema might not be created
- Check Supabase dashboard > Table Editor
- Re-run `schema.sql`

---

## 📊 Verify Everything Works

### Check Database

1. Go to Supabase Dashboard
2. Click "Table Editor"
3. Click `documents` table
4. ✅ Should see rows with your data

### Check API

```bash
# Health check
curl http://localhost:8000/

# Chat endpoint
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query":"Tell me about SFSU CS"}'
```

### Check Frontend

1. Open http://localhost:5173
2. Chat interface loads ✅
3. Can send messages ✅
4. Gets responses ✅

---

## 🎯 Next Steps

Once everything works locally:

1. **Change default password**:
   - Login as admin@sfsu.edu
   - Go to Settings
   - Change password

2. **Add more professors**:
   - Go to Supabase > Table Editor > professors
   - Click "Insert" > "Insert row"
   - Use this Python script to hash password:
   ```python
   from passlib.context import CryptContext
   pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
   print(pwd_context.hash("new_password"))
   ```

3. **Deploy to production** (see DEPLOYMENT.md)

---

## 🆘 Need Help?

Common issues:

| Problem | Solution |
|---------|----------|
| "Module not found" | Run `pip install -r requirements.txt` |
| "Port 8000 already in use" | Kill other process or use different port |
| "Database schema not found" | Run `schema.sql` in Supabase SQL Editor |
| Frontend blank page | Check browser console for errors |
| No responses from chat | Check backend logs, verify database has data |

---

## ✅ Success Checklist

- [ ] Database schema created in Supabase
- [ ] Data migrated successfully
- [ ] Backend runs without errors
- [ ] Can chat and get responses
- [ ] Professor login works
- [ ] Can see and update corrections
- [ ] Ready for deployment!

**If all checkboxes are checked, you're ready to deploy! 🚀**
