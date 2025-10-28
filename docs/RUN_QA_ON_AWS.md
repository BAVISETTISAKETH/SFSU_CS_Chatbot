# Run Q&A Generation on Your Existing AWS Instance

## Perfect! You can use your existing AWS EC2 instance

### Advantages of Using Your AWS Instance:
- ✅ Already set up
- ✅ No PC load/overheating
- ✅ Likely has good specs
- ✅ Can run for hours without interruption
- ✅ Fast network for downloading models

---

## Step 1: Connect to Your AWS Instance

```bash
# From your local PC
ssh -i your-key.pem ubuntu@your-aws-ip

# Or if you have Windows and used yesterday's setup:
ssh ubuntu@your-aws-ip
```

---

## Step 2: Install Ollama on AWS

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama service
ollama serve &

# Wait a moment, then pull the model
ollama pull llama3.2

# Test it
ollama run llama3.2 "Say hello"
```

---

## Step 3: Upload Your Files to AWS

### Option A: Using SCP (from your PC)

```bash
# Upload the data file
scp -i your-key.pem D:\sfsu-cs-chatbot\data\comprehensive_sfsu_crawl.json ubuntu@your-aws-ip:~/

# Upload the generation script
scp -i your-key.pem D:\sfsu-cs-chatbot\generate_qa_with_ollama.py ubuntu@your-aws-ip:~/
```

### Option B: Using git (if your repo is on GitHub)

```bash
# On AWS instance
git clone your-repo-url
cd sfsu-cs-chatbot
```

### Option C: Download from your Supabase/S3 (if you uploaded there)

```bash
# If you stored the file somewhere accessible
wget https://your-storage-url/comprehensive_sfsu_crawl.json
```

---

## Step 4: Set Up Python Environment on AWS

```bash
# Install Python dependencies
pip install requests python-dotenv

# Create data directory
mkdir -p data
mv comprehensive_sfsu_crawl.json data/
```

---

## Step 5: Run Q&A Generation

```bash
# Run in background so you can disconnect
nohup python generate_qa_with_ollama.py > qa_generation.log 2>&1 &

# Get the process ID
echo $!

# Monitor progress
tail -f qa_generation.log

# Or check status periodically
tail -100 qa_generation.log
```

---

## Step 6: Monitor Progress

### Check how many Q&A pairs generated so far:

```bash
# Check file size
ls -lh data/qa_training_data.json

# Count Q&A pairs
python3 -c "import json; data=json.load(open('data/qa_training_data.json')); print(f'Q&A pairs: {len(data)}')"

# Watch live updates
watch -n 30 'python3 -c "import json; data=json.load(open(\"data/qa_training_data.json\")); print(f\"Q&A pairs: {len(data)}\")"'
```

---

## Step 7: Download Results When Done

```bash
# From your local PC
scp -i your-key.pem ubuntu@your-aws-ip:~/data/qa_training_data.json D:\sfsu-cs-chatbot\data\
```

---

## Quick Copy-Paste Commands

### On Your Local PC:

```bash
# Upload files
scp D:\sfsu-cs-chatbot\data\comprehensive_sfsu_crawl.json ubuntu@YOUR_AWS_IP:~/
scp D:\sfsu-cs-chatbot\generate_qa_with_ollama.py ubuntu@YOUR_AWS_IP:~/

# SSH into AWS
ssh ubuntu@YOUR_AWS_IP
```

### On AWS Instance:

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama serve &
sleep 5
ollama pull llama3.2

# Setup
mkdir -p data
mv comprehensive_sfsu_crawl.json data/
pip install requests python-dotenv

# Run generation (in background)
nohup python3 generate_qa_with_ollama.py > qa_generation.log 2>&1 &

# Monitor
tail -f qa_generation.log

# When done, check results
ls -lh data/qa_training_data.json
```

### Download Results:

```bash
# From your local PC
scp ubuntu@YOUR_AWS_IP:~/data/qa_training_data.json D:\sfsu-cs-chatbot\data\
```

---

## What AWS Instance Type Do You Have?

### If you have GPU (g4dn, g5, p3, etc.):
- ⚡ SUPER FAST - Will process all 3,867 pages in ~15-20 minutes
- Model will use GPU automatically

### If you have CPU only (t2, t3, m5, etc.):
- ⏱️ SLOWER - Will take ~90-120 minutes
- Still works fine, just slower

### Check your instance type:

```bash
# On AWS
curl http://169.254.169.254/latest/meta-data/instance-type

# Check if GPU available
nvidia-smi

# If nvidia-smi works, you have GPU! 🎉
```

---

## Estimated Cost

### CPU Instance (t3.xlarge):
- **~$0.16/hour**
- Time: ~90 minutes
- Cost: **~$0.24**

### GPU Instance (g4dn.xlarge):
- **~$0.526/hour**
- Time: ~20 minutes
- Cost: **~$0.18**

**Both are very cheap! GPU is actually cheaper due to faster processing.**

---

## Pro Tips

### 1. Use `tmux` to Keep Session Alive

```bash
# Start tmux session
tmux new -s qa_generation

# Run generation
python3 generate_qa_with_ollama.py

# Detach: Press Ctrl+B, then D
# Reattach later: tmux attach -t qa_generation
```

### 2. Process in Parallel (If Multi-Core)

Update script to process multiple pages simultaneously:

```python
# Use ThreadPoolExecutor for parallel processing
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=4) as executor:
    # Process 4 pages at once
    ...
```

### 3. Auto-Shutdown When Done

```bash
# Add to end of generation script
# Auto-shutdown to save costs
sudo shutdown -h +5  # Shutdown in 5 minutes
```

---

## Troubleshooting

### If Ollama won't start:

```bash
# Kill any existing Ollama processes
pkill ollama

# Start fresh
ollama serve &
sleep 5
ollama pull llama3.2
```

### If out of memory:

```bash
# Check memory
free -h

# Use smaller model
ollama pull phi3  # Only 3.8GB vs llama3.2's 4GB
```

### If generation stops:

```bash
# Check if process is still running
ps aux | grep python

# Check logs
tail -100 qa_generation.log

# Resume (script has resume functionality)
python3 generate_qa_with_ollama.py
```

---

## Summary

**Using your existing AWS instance is PERFECT!**

✅ No PC overheating
✅ Already set up
✅ Fast network
✅ Can run for hours
✅ Very cheap (~$0.18-0.24)

**Quick steps:**
1. SSH to AWS
2. Install Ollama (5 min)
3. Upload data file
4. Run generation script
5. Wait ~20-90 minutes
6. Download results

**Total cost:** Less than $0.25!

Let me know if you need help with any step!
