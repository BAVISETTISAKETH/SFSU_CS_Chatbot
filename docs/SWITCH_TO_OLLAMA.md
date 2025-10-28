# 🔄 Switch from Groq to Ollama - Complete Guide

## Current Situation

Your system has **TWO** LLM services:
1. ✅ `llm_ollama.py` - Ollama (local, NO rate limits)
2. ❌ `llm.py` - Groq (API, has rate limits) **← Currently active**

But `main.py` is importing **Groq**, which is why you're hitting rate limits!

---

## Why Use Ollama Instead?

| Feature | Groq (Current) | Ollama (Should Use) |
|---------|----------------|---------------------|
| **Rate Limits** | ❌ 14 req/min | ✅ **UNLIMITED** |
| **Cost** | ❌ Free tier limited | ✅ **FREE forever** |
| **Speed** | ⚡ Very fast | ⚡ Fast (local GPU) |
| **Privacy** | ❌ Sends data to API | ✅ **All local** |
| **Internet Required** | ❌ Yes | ✅ No (offline works) |

**Verdict**: Ollama is better for your use case!

---

## Issues with Current Ollama Implementation

I checked your `llm_ollama.py` - found these issues:

1. ❌ Temperature 0.2 (should be 0.0 for zero hallucination)
2. ❌ No dual-source support
3. ❌ Not being used (main.py imports Groq)
4. ❌ Model is Mistral 7B (could use better model)

---

## Fix 1: Update main.py to Use Ollama

**File**: `backend/main.py` line 17

**Change**:
```python
# OLD (Groq):
from services.llm import LLMService

# NEW (Ollama):
from services.llm_ollama import OllamaLLMService as LLMService
```

That's it! Now it uses Ollama with **NO rate limits**.

---

## Fix 2: Update Ollama Temperature to 0.0

**File**: `backend/services/llm_ollama.py` line 139

**Change**:
```python
# OLD:
"temperature": 0.2,  # Low but not robotic

# NEW:
"temperature": 0.0,  # ZERO hallucination tolerance
```

---

## Fix 3: Ensure Ollama is Running

### Check if Ollama is Running

```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# Should return list of models
```

### If Not Running:

**Windows**:
```bash
# Start Ollama
ollama serve

# In another terminal, pull the model
ollama pull mistral:7b-instruct
```

**Alternative - Better Model**:
```bash
# Use DeepSeek-R1 (better reasoning)
ollama pull deepseek-r1:8b
```

Then update `llm_ollama.py` line 16:
```python
self.model = "deepseek-r1:8b"  # Better reasoning model
```

---

## Complete Ollama Setup Guide

### Step 1: Install Ollama (If Not Installed)

**Download**: https://ollama.com/download

**Install and Start**:
```bash
# Windows: Run the installer
# Then start Ollama
ollama serve
```

### Step 2: Pull Model

```bash
# Option A: Mistral (current)
ollama pull mistral:7b-instruct

# Option B: DeepSeek (better reasoning)
ollama pull deepseek-r1:8b

# Option C: Llama 3.2 (balanced)
ollama pull llama3.2:latest
```

### Step 3: Verify Ollama Works

```bash
# Test it
ollama run mistral:7b-instruct "Hello, how are you?"
```

Should get a response.

### Step 4: Apply the Fixes

I'll create the updated files for you.

---

## Recommended Model for SFSU Chatbot

**Best Options**:

1. **DeepSeek-R1 8B** (Recommended)
   - Excellent reasoning
   - Good at following instructions
   - Fast enough for local use
   ```bash
   ollama pull deepseek-r1:8b
   ```

2. **Mistral 7B** (Current - Good)
   - Reliable
   - Fast
   - Good for RAG
   ```bash
   ollama pull mistral:7b-instruct
   ```

3. **Llama 3.2 11B** (Best quality, slower)
   - Highest quality
   - Better understanding
   - Requires more RAM
   ```bash
   ollama pull llama3.2:11b
   ```

---

## After Switching to Ollama

### Benefits You'll Get:

✅ **NO MORE RATE LIMITS** - Ask unlimited questions
✅ **Faster responses** - No API delays
✅ **Free forever** - No API costs
✅ **More privacy** - All data stays local
✅ **Offline capable** - Works without internet

### Trade-offs:

⚠️ Slightly slower than Groq (but no rate limits!)
⚠️ Requires Ollama running locally
⚠️ Uses your GPU/CPU

---

## Quick Implementation

Let me create the fixed files for you.
