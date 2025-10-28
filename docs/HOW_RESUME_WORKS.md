# How Smart Resume Works - Zero Duplicates Guaranteed!

## Your Concern (Valid!)
- 4,000 pages in ONE big JSON file (`comprehensive_sfsu_crawl.json`)
- Process 1/4 today (1,000 pages)
- Process another 1/4 tomorrow (another 1,000 pages)
- **Question:** How does it know which pages were already processed?

---

## The Answer: URL Tracking System ✅

The script uses **source URLs** to track which pages have been processed. Here's exactly how it works:

### Step-by-Step Process:

## Day 1 (Today) - First Run

**1. Script starts:**
```
[RESUME] Checking for existing Q&A data...
[RESUME] No existing data found - starting fresh
```

**2. Loads input file:**
```
[LOAD] Loading scraped data from: comprehensive_sfsu_crawl.json
[DATA] Loaded 4000 scraped pages
```

**3. No URLs to skip (first run):**
```python
processed_urls = set()  # Empty set - nothing processed yet
```

**4. Processes 1,000 pages:**
```
[1/1000] Processing: CS Department Homepage
   URL: https://cs.sfsu.edu/
   [OK] +3 Q&A pairs

[2/1000] Processing: Graduate Programs
   URL: https://cs.sfsu.edu/graduate-programs
   [OK] +2 Q&A pairs

... continues for 1,000 pages ...
```

**5. Saves output with URLs:**
```json
// data/qa_training_data.json
[
  {
    "question": "What is the CS department?",
    "answer": "...",
    "category": "cs_general",
    "source_url": "https://cs.sfsu.edu/"  ← TRACKED!
  },
  {
    "question": "What graduate programs are offered?",
    "answer": "...",
    "category": "cs_graduate",
    "source_url": "https://cs.sfsu.edu/graduate-programs"  ← TRACKED!
  },
  ... ~2,000 Q&A pairs total ...
]
```

**Result Day 1:**
- ✅ 1,000 pages processed
- ✅ ~2,000 Q&A pairs saved
- ✅ All source URLs saved in output file

---

## Day 2 (Tomorrow) - Resume Run

**1. Script starts:**
```
[RESUME] Checking for existing Q&A data...
[RESUME] Found 2,000 existing Q&A pairs from 1,000 pages  ← LOADS PREVIOUS WORK!
```

**2. Extracts processed URLs:**
```python
# Code from lines 218-221:
if resume and os.path.exists(output_file):
    with open(output_file, 'r', encoding='utf-8') as f:
        existing_qa_pairs = json.load(f)  # Load all previous Q&A
        processed_urls = {qa.get('source_url') for qa in existing_qa_pairs}
        # processed_urls = {
        #     "https://cs.sfsu.edu/",
        #     "https://cs.sfsu.edu/graduate-programs",
        #     ... 998 more URLs
        # }
```

**3. Filters out already-processed pages:**
```python
# Code from lines 233-235:
valid_pages = [p for p in pages
               if p.get('status') == 'success' and
                  p.get('full_text') and
                  len(p.get('full_text', '')) > 200 and
                  p.get('url') not in processed_urls]  ← SKIPS PROCESSED URLs!
```

**4. Shows filtered count:**
```
[LOAD] Loading scraped data from: comprehensive_sfsu_crawl.json
[DATA] Loaded 4000 scraped pages
[FILTER] 3000 pages available for processing (excluding already processed)
                                               ↑ Only new pages!
```

**5. Processes ONLY new pages:**
```
[1/1000] Processing: Financial Aid Overview
   URL: https://financial.sfsu.edu/aid  ← NEW URL (not in processed_urls)
   [OK] +3 Q&A pairs

[2/1000] Processing: Housing Options
   URL: https://housing.sfsu.edu/options  ← NEW URL
   [OK] +2 Q&A pairs

... continues for 1,000 MORE pages ...
```

**6. Combines old + new:**
```python
# Code from line 254:
all_qa_pairs = existing_qa_pairs.copy()  # Start with Day 1's 2,000 pairs
# Then add new pairs as they're generated
all_qa_pairs.extend(qa_pairs)  # Add Day 2's new pairs
```

**7. Saves combined data:**
```json
// data/qa_training_data.json (OVERWRITTEN with combined data)
[
  // Day 1 pairs (2,000 from 1,000 pages):
  {
    "source_url": "https://cs.sfsu.edu/",
    ...
  },
  {
    "source_url": "https://cs.sfsu.edu/graduate-programs",
    ...
  },

  // Day 2 NEW pairs (2,000 from 1,000 new pages):
  {
    "source_url": "https://financial.sfsu.edu/aid",  ← NEW!
    ...
  },
  {
    "source_url": "https://housing.sfsu.edu/options",  ← NEW!
    ...
  },
  ... ~4,000 Q&A pairs total ...
]
```

**Result Day 2:**
- ✅ 1,000 NEW pages processed (skipped the first 1,000)
- ✅ ~4,000 Q&A pairs total (2,000 old + 2,000 new)
- ✅ ZERO duplicates!

---

## Visual Diagram

```
Day 1:
comprehensive_sfsu_crawl.json (4,000 pages)
├── Page 1: cs.sfsu.edu/ ──────────────► PROCESSED ✓
├── Page 2: cs.sfsu.edu/graduate ──────► PROCESSED ✓
├── Page 3: cs.sfsu.edu/faculty ───────► PROCESSED ✓
├── ... (997 more)
├── Page 1000: bulletin.sfsu.edu/cs ───► PROCESSED ✓
│
├── Page 1001: financial.sfsu.edu ─────► NOT YET
├── Page 1002: housing.sfsu.edu ───────► NOT YET
├── ... (2,998 more)
└── Page 4000: news.sfsu.edu/... ──────► NOT YET

qa_training_data.json saved with:
- URLs from Pages 1-1000 tracked
- 2,000 Q&A pairs


Day 2:
Script loads qa_training_data.json
Extracts processed URLs: {cs.sfsu.edu/, cs.sfsu.edu/graduate, ...}

comprehensive_sfsu_crawl.json (4,000 pages)
├── Page 1: cs.sfsu.edu/ ──────────────► SKIP (already processed)
├── Page 2: cs.sfsu.edu/graduate ──────► SKIP (already processed)
├── ... (998 more) ────────────────────► SKIP (already processed)
├── Page 1000: bulletin.sfsu.edu/cs ───► SKIP (already processed)
│
├── Page 1001: financial.sfsu.edu ─────► PROCESS NOW ✓
├── Page 1002: housing.sfsu.edu ───────► PROCESS NOW ✓
├── ... (998 more) ────────────────────► PROCESS NOW ✓
├── Page 2000: registrar.sfsu.edu ─────► PROCESS NOW ✓
│
├── Page 2001: career.sfsu.edu ────────► NOT YET
└── ... remaining pages

qa_training_data.json updated with:
- OLD: Pages 1-1000 (kept)
- NEW: Pages 1001-2000 (added)
- Total: 4,000 Q&A pairs
```

---

## How Duplicates Are IMPOSSIBLE

### The URL Set Check:

```python
# Line 235: The key line that prevents duplicates
p.get('url') not in processed_urls
```

**Before processing each page:**
1. Get page URL: `"https://cs.sfsu.edu/"`
2. Check if URL in `processed_urls` set
3. If YES → Skip this page (already done)
4. If NO → Process this page

**Set lookup is O(1)** - instant check, no duplicates possible!

---

## Real Example from Your Data

Let's say today's run generated this:

```json
[
  {
    "question": "What is the Computer Science Department?",
    "answer": "The CS department at SFSU offers...",
    "source_url": "https://cs.sfsu.edu/"
  },
  {
    "question": "What MS programs are available?",
    "answer": "SFSU offers MS in Computer Science...",
    "source_url": "https://cs.sfsu.edu/graduate-programs"
  }
]
```

Tomorrow, when you run again:

```python
# Script loads the above file
processed_urls = {
    "https://cs.sfsu.edu/",
    "https://cs.sfsu.edu/graduate-programs"
}

# Then filters the 4,000 pages:
for page in all_4000_pages:
    if page['url'] == "https://cs.sfsu.edu/":
        # SKIP - already in processed_urls set!
        continue

    if page['url'] == "https://cs.sfsu.edu/graduate-programs":
        # SKIP - already in processed_urls set!
        continue

    if page['url'] == "https://housing.sfsu.edu/":
        # PROCESS - NOT in processed_urls set!
        process_this_page()
```

---

## Auto-Save Checkpoints (Extra Safety)

Even within a single run, progress is saved every 10 pages:

```python
# Code from lines 292-296:
if i % 10 == 0:
    print(f"\n[SAVE] Progress checkpoint: {len(all_qa_pairs)} Q&A pairs")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_qa_pairs, f, indent=2, ensure_ascii=False)
```

**What this means:**
- If script crashes at page 347, you've saved up to page 340
- Next run skips pages 1-340 automatically
- Resumes from page 341
- No wasted work!

---

## Testing the Resume Feature

You can verify this works right now:

```powershell
# Check current Q&A data
python -c "import json; data=json.load(open('data/qa_training_data.json')); print(f'{len(data)} Q&A pairs from {len(set(qa[\"source_url\"] for qa in data))} unique pages')"

# Expected output:
# 105 Q&A pairs from 35 unique pages
```

When you run the script again tomorrow:

```powershell
venv/Scripts/python.exe generate_qa_multi_provider.py
```

You'll see:
```
[RESUME] Found 105 existing Q&A pairs from 35 pages
[FILTER] 3965 pages available for processing (excluding already processed)
```

**3965 = 4000 - 35** ← Perfect! Those 35 pages are skipped!

---

## Summary

**Question:** How does it avoid duplicates?

**Answer:**
1. ✅ Every Q&A pair stores `source_url`
2. ✅ On resume, script loads all previous `source_url`s into a set
3. ✅ Before processing, checks: `if url not in processed_urls`
4. ✅ Only processes pages NOT in the set
5. ✅ Combines old + new Q&A pairs
6. ✅ Saves everything to same file

**Result:** ZERO duplicates, 100% guaranteed! 🎉

---

## Your 4-Day Plan (No Duplicates)

**Day 1 (Today):**
- Process: 1,000 new pages
- Save: 2,000 Q&A pairs
- Tracked URLs: 1,000

**Day 2 (Tomorrow):**
- Skip: 1,000 already-processed pages
- Process: 1,000 NEW pages
- Save: 4,000 Q&A pairs total (2,000 old + 2,000 new)
- Tracked URLs: 2,000

**Day 3:**
- Skip: 2,000 already-processed pages
- Process: 1,000 NEW pages
- Save: 6,000 Q&A pairs total
- Tracked URLs: 3,000

**Day 4:**
- Skip: 3,000 already-processed pages
- Process: 1,000 NEW pages
- Save: 8,000 Q&A pairs total
- Tracked URLs: 4,000 ✅ **COMPLETE!**

**Zero duplicates at any step!**
