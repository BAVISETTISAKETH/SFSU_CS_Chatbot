# Fix "High Demand" Error - Rate Limiting Solution

## Problem

After ~10 questions, you see: **"I am currently experiencing high demand. Please wait a moment and try again."**

**Root Cause**: Groq Free Tier Rate Limits
- **14 requests per minute**
- **14,400 tokens per minute**
- Current code has simple delay (4.5s) but doesn't properly handle bursts

## Solutions (Choose One)

---

### Solution 1: Increase Wait Time (QUICK FIX - 2 minutes)

**Best for**: Quick fix while keeping free tier

Edit `backend/services/llm.py`:

```python
# Line 27: Change from 4.5 to 6 seconds
self.min_request_interval = 6.0  # 6 seconds = ~10 requests/min (safer)
```

**Impact**:
- Slower responses when asking multiple questions quickly
- But won't hit rate limit
- Free tier still works

---

### Solution 2: Implement Proper Rate Limiter (RECOMMENDED - 5 minutes)

**Best for**: Production use with better UX

I'll create an improved rate limiter that:
- Tracks requests over rolling 60-second window
- Provides better error messages
- Shows wait time to user

---

### Solution 3: Upgrade to Groq Paid Tier (BEST - $$$)

**Best for**: Production deployment

Groq Pay-as-you-go:
- **30 requests per minute** (2x free tier)
- **Unlimited tokens**
- Very affordable (~$0.50-2/day for moderate use)

Sign up: https://console.groq.com/

Add to `.env`:
```bash
GROQ_API_KEY=gsk_xxxxx  # Your paid tier key
```

---

## Quick Fix Implementation (Solution 1)

### Step 1: Edit Rate Limit

```bash
# Open file
code backend/services/llm.py

# Find line 27:
self.min_request_interval = 4.5

# Change to:
self.min_request_interval = 6.0  # Safer for free tier
```

### Step 2: Restart Backend

```bash
cd backend
..\venv\Scripts\python.exe main.py
```

### Step 3: Test

Ask 10-15 questions rapidly. Should work without errors!

---

## Advanced Fix (Solution 2) - Better Rate Limiter

I'll create a smarter rate limiter for you.
