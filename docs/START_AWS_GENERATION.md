# SFSU Q&A Generation on AWS - READY TO RUN

## ✅ CONFIRMED - MAXIMUM EXTRACTION MODE

**Your scripts are now updated to extract MAXIMUM Q&A pairs from each page!**

### What Changed:
- ❌ OLD: 2-3 Q&A pairs per page
- ✅ NEW: 5-10+ Q&A pairs per page (as many as possible!)
- ✅ Long pages split into chunks (2500 char chunks with overlap)
- ✅ Each chunk processed separately
- ✅ Increased token limit: 1500 → 4000 tokens
- ✅ Better prompts: "Extract EVERY possible question"

**Expected Result:**
- **OLD:** ~2,800 Q&A pairs (2.8 per page × 1000 pages)
- **NEW:** ~15,000-30,000 Q&A pairs (5-10 per page × 3,867 pages)

---

## Your AWS Instance

**IP:** `3.145.143.107`
**Type:** T3 (CPU-optimized)
**Region:** US-East (Ohio)

---

## STEP-BY-STEP INSTRUCTIONS

### Step 1: Connect to AWS

Open PowerShell on your PC and run:

```powershell
ssh ubuntu@3.145.143.107
```

If asked "Are you sure you want to continue connecting?", type **yes**

---

### Step 2: Install Ollama on AWS

Once connected, copy-paste this entire block:

```bash
echo "Installing Ollama..."
curl -fsSL https://ollama.com/install.sh | sh

echo "Starting Ollama server..."
nohup ollama serve > ollama.log 2>&1 &

sleep 10

echo "Downloading llama3.2 model (takes ~2 minutes)..."
ollama pull llama3.2

echo "Installing Python packages..."
pip3 install requests python-dotenv

mkdir -p data

echo "✅ Setup complete!"
```

**Wait time:** ~5 minutes

---

### Step 3: Upload Files from Your PC

Open a **NEW PowerShell window** (keep AWS terminal open):

```powershell
# Upload data file (this is the large file, takes ~1 minute)
scp D:\sfsu-cs-chatbot\data\comprehensive_sfsu_crawl.json ubuntu@3.145.143.107:~/data/

# Upload generation script
scp D:\sfsu-cs-chatbot\generate_qa_with_ollama.py ubuntu@3.145.143.107:~/
```

**Wait for both uploads to complete!**

---

### Step 4: Start Q&A Generation

Back in your AWS terminal:

```bash
# Start generation in background
nohup python3 generate_qa_with_ollama.py > qa_generation.log 2>&1 &

echo "✅ Generation started!"
echo "Monitor with: tail -f qa_generation.log"
```

---

### Step 5: Monitor Progress

```bash
# Watch live output (Ctrl+C to stop watching, process keeps running)
tail -f qa_generation.log

# Or check periodically:
tail -50 qa_generation.log

# Count Q&A pairs generated so far:
python3 -c "import json; data=json.load(open('data/qa_training_data.json')); print(f'Generated: {len(data)} Q&A pairs')"
```

---

### Step 6: You Can Disconnect!

**The process runs in background with `nohup`**

You can:
- ✅ Close AWS terminal
- ✅ Turn off your PC
- ✅ Come back later

To check back later:
```bash
ssh ubuntu@3.145.143.107
tail -50 qa_generation.log
```

---

### Step 7: Download Results (When Done)

From your PC:

```powershell
# Download the results
scp ubuntu@3.145.143.107:~/data/qa_training_data.json D:\sfsu-cs-chatbot\data\
```

---

## Expected Performance

### With T3 Instance:

| T3 Size | vCPUs | Time Estimate | Cost | Q&A Pairs Expected |
|---------|-------|---------------|------|-------------------|
| t3.medium | 2 | ~3-4 hours | $0.80 | 15,000-30,000 |
| t3.large | 2 | ~2-3 hours | $0.40 | 15,000-30,000 |
| t3.xlarge | 4 | ~1.5-2 hours | $0.30 | 15,000-30,000 |

**Check your instance type:**
```bash
curl -s http://169.254.169.254/latest/meta-data/instance-type
```

---

## Quick Copy-Paste Commands

### From Your PC (PowerShell):

**Connect:**
```powershell
ssh ubuntu@3.145.143.107
```

**Upload Files (in NEW PowerShell window):**
```powershell
scp D:\sfsu-cs-chatbot\data\comprehensive_sfsu_crawl.json ubuntu@3.145.143.107:~/data/
scp D:\sfsu-cs-chatbot\generate_qa_with_ollama.py ubuntu@3.145.143.107:~/
```

**Download Results (when done):**
```powershell
scp ubuntu@3.145.143.107:~/data/qa_training_data.json D:\sfsu-cs-chatbot\data\
```

---

### On AWS Instance:

**Setup (one-time):**
```bash
curl -fsSL https://ollama.com/install.sh | sh && nohup ollama serve > /dev/null 2>&1 & sleep 10 && ollama pull llama3.2 && pip3 install requests python-dotenv && mkdir -p data
```

**Start Generation:**
```bash
nohup python3 generate_qa_with_ollama.py > qa_generation.log 2>&1 &
tail -f qa_generation.log
```

**Check Progress:**
```bash
python3 -c "import json; data=json.load(open('data/qa_training_data.json')); print(f'Q&A pairs: {len(data)}')"
```

---

## What You'll See During Generation

```
[1/3867] SF State receives $14M from Genentech Foundation...
   Processing 3 chunks...
   [OK] +12 Q&A pairs (Total: 12)
[2/3867] Study Abroad programs...
   Processing 2 chunks...
   [OK] +8 Q&A pairs (Total: 20)
[3/3867] Division of International Education...
   [OK] +6 Q&A pairs (Total: 26)
...
```

**Notice:** Pages now generate **5-12+ Q&A pairs** instead of 2-3!

---

## Troubleshooting

### Can't connect to AWS?
```bash
# Check if instance is running in AWS Console
# Security group should allow port 22 (SSH)
```

### Ollama not starting?
```bash
pkill ollama
ollama serve &
sleep 5
ollama pull llama3.2
```

### Generation stopped?
```bash
# Check if process is running
ps aux | grep python3

# Resume (script has auto-resume)
python3 generate_qa_with_ollama.py
```

---

## Summary

✅ **Maximum extraction enabled** - 5-10+ Q&A pairs per page
✅ **AWS IP ready:** 3.145.143.107
✅ **Expected output:** 15,000-30,000 Q&A pairs
✅ **Time:** 1.5-4 hours depending on instance
✅ **Cost:** $0.30-0.80 total
✅ **No PC overheating**

**Ready to start? Follow Steps 1-4 above!** 🚀
