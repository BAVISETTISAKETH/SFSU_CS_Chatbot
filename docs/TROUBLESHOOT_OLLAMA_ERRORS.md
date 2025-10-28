# 🔧 Troubleshooting Ollama Errors - Quick Fix

## Error: "Sorry, encountering errors"

This means Ollama isn't running properly. Let's fix it!

---

## ⚡ Quick Fix (Choose Your Scenario)

### Scenario 1: Ollama Not Installed

**Check**:
```bash
ollama --version
```

**If "command not found"** → Install Ollama:
1. Download: https://ollama.com/download/windows
2. Run installer
3. Continue to Scenario 2

---

### Scenario 2: Ollama Installed But Not Running

**Fix**:
```bash
# Start Ollama service
ollama serve
```

**Keep this terminal open!** Ollama needs to stay running.

Then in a **NEW terminal**:
```bash
# Pull the model
ollama pull mistral:7b-instruct
```

Wait for download (~4GB, 2-3 minutes)

---

### Scenario 3: Model Not Pulled

**Check**:
```bash
ollama list
```

**If mistral NOT in list**:
```bash
ollama pull mistral:7b-instruct
```

---

## ✅ Step-by-Step Complete Fix

### Terminal 1: Start Ollama
```bash
ollama serve
```

**Keep this running!** You should see:
```
Ollama is running
```

---

### Terminal 2: Pull Model
```bash
ollama pull mistral:7b-instruct
```

**Wait for**:
```
pulling manifest
pulling ... 100%
verifying sha256 digest
success
```

---

### Terminal 3: Verify It Works
```bash
ollama run mistral:7b-instruct "Hello"
```

**Should get a response**. If yes, press Ctrl+D to exit.

---

### Terminal 4: Start Backend
```bash
cd D:\sfsu-cs-chatbot\backend
..\venv\Scripts\python.exe main.py
```

**Look for**:
```
[OK] LLM Service (Ollama - LOCAL, NO RATE LIMITS): True
```

**If you see "False"** → Go back to Terminal 1, make sure `ollama serve` is running

---

## ✅ Quick Verification

### Test 1: Is Ollama Running?
```bash
curl http://localhost:11434/api/tags
```

**Should return JSON**. If error → Ollama not running

---

### Test 2: Is Model Available?
```bash
ollama list
```

**Should show**:
```
NAME                     ID          SIZE
mistral:7b-instruct     ...         4.1 GB
```

---

### Test 3: Can Ollama Respond?
```bash
ollama run mistral:7b-instruct "Say hello"
```

**Should get response**. Press Ctrl+D to exit.

---

### Test 4: Backend Sees Ollama?

**Check backend startup logs**:
```
[OK] LLM Service (Ollama - LOCAL, NO RATE LIMITS): True
```

If **False** → Ollama isn't running or model not pulled

---

## 🐛 Common Issues & Fixes

### Issue 1: "Connection refused to localhost:11434"

**Fix**:
```bash
# Terminal 1 - Start Ollama
ollama serve

# Keep it running!
```

---

### Issue 2: "Model not found"

**Fix**:
```bash
ollama pull mistral:7b-instruct
```

---

### Issue 3: Backend still shows "False"

**Fix**:
```bash
# 1. Stop backend (Ctrl+C)

# 2. Verify Ollama running:
curl http://localhost:11434/api/tags

# 3. Restart backend:
cd backend
..\venv\Scripts\python.exe main.py
```

---

### Issue 4: Download stuck

**Fix**:
```bash
# Cancel (Ctrl+C)
# Try again:
ollama pull mistral:7b-instruct
```

---

## 🔄 Complete Reset (If Nothing Works)

### Step 1: Stop Everything
```bash
# Stop backend (Ctrl+C in backend terminal)
# Stop Ollama (Ctrl+C in ollama serve terminal)
```

### Step 2: Start Fresh
```bash
# Terminal 1:
ollama serve

# Wait for "Ollama is running"
```

### Step 3: Pull Model
```bash
# Terminal 2:
ollama pull mistral:7b-instruct

# Wait for "success"
```

### Step 4: Test
```bash
# Terminal 2:
ollama list

# Should show mistral:7b-instruct
```

### Step 5: Start Backend
```bash
# Terminal 3:
cd D:\sfsu-cs-chatbot\backend
..\venv\Scripts\python.exe main.py

# Look for:
# [OK] LLM Service (Ollama - LOCAL, NO RATE LIMITS): True
```

### Step 6: Test Chat
Open frontend: http://localhost:5173

Ask: "Hello, can you help me?"

**Should work!**

---

## 📋 Checklist

Before asking questions, verify:

- [ ] `ollama serve` is running in a terminal
- [ ] `ollama list` shows `mistral:7b-instruct`
- [ ] `curl http://localhost:11434/api/tags` returns JSON
- [ ] Backend shows `[OK] LLM Service: True`
- [ ] Backend is running on port 8000
- [ ] Frontend is running on port 5173

**If all checked** → Chat should work!

---

## 🆘 Still Not Working?

### Check Backend Logs

Look at the backend terminal for errors like:

**Error 1**: "Connection refused"
```
[ERROR] Error generating response: Connection refused
```
**Fix**: Start `ollama serve`

**Error 2**: "Model not found"
```
[ERROR] Model mistral:7b-instruct not found
```
**Fix**: Run `ollama pull mistral:7b-instruct`

**Error 3**: "Timeout"
```
[ERROR] Timeout connecting to Ollama
```
**Fix**: Ollama is slow to start, wait 30 seconds and try again

---

## ✅ Expected Working Setup

When everything is working:

**Terminal 1** (Ollama):
```
Ollama is running
```

**Terminal 2** (Backend):
```
[OK] LLM Service (Ollama - LOCAL, NO RATE LIMITS): True
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Terminal 3** (Frontend):
```
VITE ready in 500 ms
➜  Local: http://localhost:5173/
```

**Browser**: Chat works, no errors!

---

## 🎯 Most Common Fix

**90% of the time, this fixes it**:

```bash
# Terminal 1:
ollama serve

# Terminal 2:
ollama pull mistral:7b-instruct

# Terminal 3:
cd backend
..\venv\Scripts\python.exe main.py
```

Then refresh browser and try chatting!

---

**Need more help?** Share the exact error message from the backend terminal!
