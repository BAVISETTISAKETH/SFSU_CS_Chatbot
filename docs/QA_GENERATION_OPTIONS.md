# Q&A Generation Options - Current Status

**Date:** October 17, 2025
**Current Q&A Pairs:** 105 (from 35 pages)
**Total Pages Available:** 4,000
**Target:** 500-1,000+ Q&A pairs

---

## Current Situation

We've successfully generated **105 high-quality Q&A pairs** using Groq's free tier, but hit the rate limit. The Groq free tier resets every 24 hours.

**Good news:** The new script (`generate_qa_multi_provider.py`) has smart resume capability - it remembers which pages were already processed and won't duplicate work!

---

## Option 1: Continue with Groq (FREE) ⭐ RECOMMENDED

**Cost:** $0
**Time:** 5-7 days to process all 4,000 pages
**Quality:** Excellent (llama-3.3-70b-versatile)

### How it works:
- Process ~100-150 pages per day (free tier limit)
- Generate ~200-300 Q&A pairs per day
- Run the script once per day for a week
- Total: 1,000-1,500 Q&A pairs in 5-7 days

### Daily workflow:
```powershell
# Run once per day (takes 5-10 minutes per session)
venv/Scripts/python.exe generate_qa_multi_provider.py
```

**Benefits:**
- ✅ Completely FREE
- ✅ No credit card needed
- ✅ High quality results
- ✅ Auto-resumes from where you left off
- ✅ More than enough for chatbot training

**Next run:** October 18, 2025 (24 hours after first run)

---

## Option 2: OpenAI API (PAID)

**Cost:** ~$8-15 for 4,000 pages
**Time:** 1-2 hours (complete today)
**Model:** gpt-4o-mini (cheaper) or gpt-4o (better quality)

### Setup:
1. Go to https://platform.openai.com/api-keys
2. Create an account and add payment method
3. Generate API key (starts with `sk-proj-...`)
4. Add to `.env` file:
   ```
   OPENAI_API_KEY=sk-proj-your-key-here
   ```
5. Install package:
   ```powershell
   venv/Scripts/pip install openai
   ```
6. Run script:
   ```powershell
   venv/Scripts/python.exe generate_qa_multi_provider.py
   ```

**Pricing (estimated):**
- gpt-4o-mini: $0.150/1M input tokens, $0.600/1M output tokens
- For 4,000 pages: ~$8-12 total
- For 500 pages: ~$1-2

**Benefits:**
- ✅ Finish everything today
- ✅ Very high quality
- ✅ Fast processing
- ✅ Higher rate limits

**Note:** ChatGPT Plus subscription does NOT include API access. API is separate billing.

---

## Option 3: Anthropic API (PAID)

**Cost:** ~$10-20 for 4,000 pages
**Time:** 1-2 hours (complete today)
**Model:** claude-3-5-haiku (fast) or claude-3-5-sonnet (best quality)

### Setup:
1. Go to https://console.anthropic.com/
2. Create account and add payment
3. Generate API key (starts with `sk-ant-...`)
4. Add to `.env` file:
   ```
   ANTHROPIC_API_KEY=sk-ant-your-key-here
   ```
5. Install package:
   ```powershell
   venv/Scripts/pip install anthropic
   ```
6. Run script:
   ```powershell
   venv/Scripts/python.exe generate_qa_multi_provider.py
   ```

**Pricing (estimated):**
- Claude 3.5 Haiku: $1/M input, $5/M output
- For 4,000 pages: ~$10-15 total
- For 500 pages: ~$2-3

**Benefits:**
- ✅ Finish everything today
- ✅ Excellent quality (Claude is very good)
- ✅ Fast processing
- ✅ Higher rate limits

**Note:** Claude Pro subscription does NOT include API access. API is separate billing.

---

## Comparison Table

| Option | Cost | Time | Quality | Effort |
|--------|------|------|---------|--------|
| **Groq (free)** | $0 | 5-7 days | Excellent | Run once/day |
| **OpenAI** | $8-15 | 1-2 hours | Excellent | One-time setup |
| **Anthropic** | $10-20 | 1-2 hours | Excellent | One-time setup |

---

## Recommended Strategy

### For Most Users: **Option 1 (Groq - FREE)** ⭐

**Why this is best:**
1. **Completely free** - No credit card needed
2. **105 Q&A pairs is already useful** - Can start testing chatbot improvement today
3. **5-7 days is reasonable** - Run script once per day while having morning coffee
4. **Auto-resume works perfectly** - No risk of duplicate work
5. **Quality is excellent** - llama-3.3-70b is very capable

**Daily routine:**
```powershell
# Every day at roughly the same time:
cd D:\sfsu-cs-chatbot
venv\Scripts\activate
python generate_qa_multi_provider.py

# Takes 5-10 minutes, generates ~200-300 Q&A pairs
# Check progress in data/qa_training_data.json
```

### When to use paid APIs:

**Use OpenAI/Anthropic if:**
- You need to finish TODAY (urgent deadline)
- You have API credits already
- $10-20 is not a concern
- You want to test immediately with full dataset

---

## What You Have Right Now

**File:** `data/qa_training_data.json`
**Q&A Pairs:** 105
**Quality:** High (verified samples look good)

### You can start using these 105 pairs today!

Even with just 105 Q&A pairs, you'll see improvement in chatbot accuracy for common questions. The script's smart resume feature means you can:

1. **Upload 105 pairs to Supabase today** ✅
2. **Integrate into chatbot** ✅
3. **Test improvement** ✅
4. **Add more Q&A pairs daily** ✅

---

## How to Upload Current 105 Q&A Pairs to Supabase

You can start benefiting from the 105 pairs immediately:

### Step 1: Create Supabase Table
Go to Supabase Dashboard → SQL Editor:

```sql
CREATE TABLE IF NOT EXISTS qa_training (
    id BIGSERIAL PRIMARY KEY,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    category TEXT,
    source_url TEXT,
    question_embedding VECTOR(384),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for fast vector search
CREATE INDEX IF NOT EXISTS idx_qa_training_embedding
ON qa_training USING ivfflat (question_embedding vector_cosine_ops)
WITH (lists = 100);

-- Create text search index
CREATE INDEX IF NOT EXISTS idx_qa_training_question
ON qa_training USING gin(to_tsvector('english', question));

-- Create search function
CREATE OR REPLACE FUNCTION match_qa_training(
    query_embedding VECTOR(384),
    match_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 5
)
RETURNS TABLE (
    id BIGINT,
    question TEXT,
    answer TEXT,
    category TEXT,
    source_url TEXT,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        qa_training.id,
        qa_training.question,
        qa_training.answer,
        qa_training.category,
        qa_training.source_url,
        1 - (qa_training.question_embedding <=> query_embedding) AS similarity
    FROM qa_training
    WHERE 1 - (qa_training.question_embedding <=> query_embedding) > match_threshold
    ORDER BY similarity DESC
    LIMIT match_count;
END;
$$;
```

### Step 2: Upload Q&A Pairs
```powershell
venv/Scripts/python.exe upload_qa_training_data.py
```

### Step 3: Integrate into Chatbot
Update `backend/main.py` to search Q&A training data first, then fall back to web search + RAG.

---

## Progress Tracking

### Day 1 (Today): ✅
- [x] Generated 105 Q&A pairs
- [x] Created multi-provider script with auto-resume
- [ ] Upload 105 pairs to Supabase (optional - can start today)
- [ ] Integrate into chatbot (optional - can start today)

### Days 2-7 (If using free Groq):
- [ ] Day 2: ~300 Q&A pairs total
- [ ] Day 3: ~500 Q&A pairs total
- [ ] Day 4: ~700 Q&A pairs total
- [ ] Day 5: ~900 Q&A pairs total
- [ ] Day 6: ~1,100 Q&A pairs total
- [ ] Day 7: ~1,300 Q&A pairs total ✅ COMPLETE

**Or complete in 1-2 hours with OpenAI/Anthropic API.**

---

## Summary

**My recommendation:** Start with Groq (free) and run it daily for a week. This gives you:

1. ✅ Zero cost
2. ✅ Can start testing with 105 pairs TODAY
3. ✅ Add more pairs daily (script auto-resumes)
4. ✅ 1,000+ pairs in a week
5. ✅ Production-ready chatbot in 1 week

**If urgent:** Get OpenAI API key, spend $8-12, finish in 1-2 hours.

---

## Next Steps (Choose Your Path)

### Path A: Free (Groq) - Recommended ⭐
```powershell
# Tomorrow (Oct 18, 2025):
venv/Scripts/python.exe generate_qa_multi_provider.py

# Repeat daily for 5-7 days
# Each run takes 5-10 minutes
# Generates ~200-300 pairs per day
```

### Path B: Paid (OpenAI)
```powershell
# Setup (one-time):
# 1. Get API key from https://platform.openai.com/api-keys
# 2. Add to .env: OPENAI_API_KEY=sk-proj-...
venv/Scripts/pip install openai

# Run (completes in 1-2 hours):
venv/Scripts/python.exe generate_qa_multi_provider.py
```

### Path C: Paid (Anthropic)
```powershell
# Setup (one-time):
# 1. Get API key from https://console.anthropic.com/
# 2. Add to .env: ANTHROPIC_API_KEY=sk-ant-...
venv/Scripts/pip install anthropic

# Run (completes in 1-2 hours):
venv/Scripts/python.exe generate_qa_multi_provider.py
```

---

## Questions?

**Q: Can I use my ChatGPT Plus subscription?**
A: No, ChatGPT Plus is web-only. API access requires separate billing ($8-15 total for this project).

**Q: Is 105 Q&A pairs enough?**
A: Yes! You can start testing chatbot improvements today with 105 pairs. Add more daily.

**Q: What if I stop halfway?**
A: No problem! The script remembers all processed pages. Just run it again anytime.

**Q: Which is best quality?**
A: All three options produce excellent quality. Groq (llama-3.3-70b), OpenAI (gpt-4o-mini), and Anthropic (claude-3.5-haiku) are all very capable.

---

**Bottom line:** Use Groq (free), run once daily for a week, get 1,000+ Q&A pairs. Or spend $10-15 to finish today.
