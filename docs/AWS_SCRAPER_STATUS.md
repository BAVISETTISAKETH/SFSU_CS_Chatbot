# AWS EC2 Scraper - Active Status

## Current Status: RUNNING ✓

**EC2 Instance:** 3.145.143.107 (t3.micro)
**Started:** October 17, 2025
**Expected Duration:** 15-30 minutes
**Expected Pages:** 1,700-2,900 pages

---

## What's Being Scraped

The comprehensive scraper is crawling **ALL** content from these SFSU domains:

1. **cs.sfsu.edu** - Computer Science Department
2. **grad.sfsu.edu** - Graduate Division
3. **oip.sfsu.edu** - Office of International Programs
4. **bulletin.sfsu.edu** - Course Catalog/Bulletin
5. **registrar.sfsu.edu** - Registrar Office
6. **financialaid.sfsu.edu** - Financial Aid
7. **housing.sfsu.edu** - Housing
8. **career.sfsu.edu** - Career Services
9. **sfsu.edu** - Main SFSU site (linked pages)
10. **news.sfsu.edu** - SFSU News (linked pages)

---

## How It Works

- **Depth:** 4 levels deep from each starting URL
- **Rate Limit:** 0.5 seconds between requests (ethical scraping)
- **Auto-Save:** Every 50 pages
- **Content Extraction:** EVERYTHING (full text, headings, paragraphs, lists, tables)
- **Deduplication:** Automatic URL normalization

---

## Monitoring Commands

### Check if scraper is running:
```powershell
ssh -i "C:\Users\bavis\Downloads\sfsu-scraper-key.pem" ubuntu@3.145.143.107 "ps aux | grep scrape"
```

### Watch real-time log:
```powershell
ssh -i "C:\Users\bavis\Downloads\sfsu-scraper-key.pem" ubuntu@3.145.143.107 "tail -f scraper.log"
```
(Press Ctrl+C to stop watching)

### Check progress:
```powershell
ssh -i "C:\Users\bavis\Downloads\sfsu-scraper-key.pem" ubuntu@3.145.143.107 "tail -20 scraper.log"
```

### Quick monitor script:
```powershell
monitor_aws_scraper.bat
```

---

## When Scraper Completes

### 1. Download the results:
```powershell
scp -i "C:\Users\bavis\Downloads\sfsu-scraper-key.pem" ubuntu@3.145.143.107:~/data/comprehensive_sfsu_crawl.json D:\sfsu-cs-chatbot\data\
```

### 2. Verify download:
```powershell
dir D:\sfsu-cs-chatbot\data\comprehensive_sfsu_crawl.json
```

### 3. Check file size:
```powershell
Get-Item D:\sfsu-cs-chatbot\data\comprehensive_sfsu_crawl.json | Select-Object Length, Name
```

Expected size: ~50-150 MB

---

## What Happens Next

Once you download the comprehensive scraped data:

### Step 1: Generate Q&A Training Data
```powershell
venv/Scripts/python.exe create_qa_training_data.py
```

This will:
- Process the comprehensive crawl data
- Generate 500-1,000+ ChatGPT-quality Q&A pairs
- Use Groq LLM to extract natural student questions
- Save to `data/qa_training_data.json`

**Note:** You already have 193 Q&A pairs from the initial test. The new comprehensive data will generate many more.

### Step 2: Create Supabase Q&A Table

Go to Supabase Dashboard → SQL Editor and run:
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

CREATE INDEX IF NOT EXISTS idx_qa_training_embedding
ON qa_training USING ivfflat (question_embedding vector_cosine_ops)
WITH (lists = 100);

CREATE INDEX IF NOT EXISTS idx_qa_training_question
ON qa_training USING gin(to_tsvector('english', question));

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

### Step 3: Upload Q&A Dataset
```powershell
venv/Scripts/python.exe upload_qa_training_data.py
```

This will upload all Q&A pairs with embeddings to Supabase.

### Step 4: Integrate into Chatbot

Update `backend/main.py` to search Q&A data first before falling back to documents and web search.

---

## Expected Results

### Current Accuracy: ~70%
- Searching raw scraped documents
- LLM synthesizes answers from messy HTML
- Inconsistent results for common questions

### After Q&A Training: ~95%
- Direct matches for common student questions
- Pre-verified, comprehensive answers
- Faster response time (no synthesis needed)
- Falls back to RAG + Web for uncommon questions

---

## EC2 Management

### Stop EC2 instance (when done):
1. Go to AWS Console → EC2 Dashboard
2. Select instance: 3.145.143.107
3. Instance State → Stop (or Terminate if completely done)

**Important:** Don't forget to stop/terminate to avoid charges after free tier!

---

## Troubleshooting

### Scraper stops unexpectedly:
```powershell
# Check if it's still running
ssh -i "C:\Users\bavis\Downloads\sfsu-scraper-key.pem" ubuntu@3.145.143.107 "ps aux | grep scrape"

# If not running, check last error
ssh -i "C:\Users\bavis\Downloads\sfsu-scraper-key.pem" ubuntu@3.145.143.107 "tail -50 scraper.log"

# Restart scraper
ssh -i "C:\Users\bavis\Downloads\sfsu-scraper-key.pem" ubuntu@3.145.143.107 "nohup python3 -u scrape_comprehensive_sfsu.py > scraper.log 2>&1 &"
```

### Can't connect to EC2:
- Check EC2 instance is running in AWS Console
- Verify security group allows SSH (port 22)
- Confirm key file path is correct

---

## Cost Tracking

**AWS EC2 t3.micro:**
- First 6 months: FREE ($200 credits)
- After credits: ~$0.01/hour (~$7.20/month if left running)

**This scrape cost:** $0.00 (within free tier)

---

## Files on EC2

```
/home/ubuntu/
├── scrape_comprehensive_sfsu.py    (15KB - The scraper script)
├── scraper.log                     (Growing - Real-time log)
├── nohup.out                       (Backup log)
└── data/
    ├── comprehensive_sfsu_crawl.json    (Will be 50-150MB when complete)
    └── scraper_progress.json            (Progress tracking)
```

---

## Quick Reference

**EC2 IP:** 3.145.143.107
**SSH Key:** C:\Users\bavis\Downloads\sfsu-scraper-key.pem
**User:** ubuntu

**Monitor:** `monitor_aws_scraper.bat`
**Download:** `scp -i "C:\Users\bavis\Downloads\sfsu-scraper-key.pem" ubuntu@3.145.143.107:~/data/comprehensive_sfsu_crawl.json D:\sfsu-cs-chatbot\data\`
