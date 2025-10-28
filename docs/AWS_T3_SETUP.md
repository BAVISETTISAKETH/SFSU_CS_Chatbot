# Running Q&A Generation on AWS T3 Instance

## Your T3 Instance is Perfect for This! ✅

T3 instances are cost-effective CPU instances that work great for this task.

---

## Complete Step-by-Step Guide

### Step 1: Connect to Your T3 Instance

From your PC (PowerShell or Command Prompt):

```bash
# Replace YOUR_AWS_IP with your actual IP
ssh ubuntu@YOUR_AWS_IP

# Or if you're using a key file:
ssh -i path/to/your-key.pem ubuntu@YOUR_AWS_IP
```

---

### Step 2: Install Ollama on T3

Copy-paste this entire block on AWS:

```bash
# Install Ollama
echo "📦 Installing Ollama..."
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama server in background
echo "🚀 Starting Ollama..."
nohup ollama serve > ollama.log 2>&1 &

# Wait for server to start
sleep 10

# Download the model (takes ~2 minutes)
echo "⬇️ Downloading model..."
ollama pull llama3.2

# Install Python dependencies
echo "📦 Installing Python packages..."
pip3 install requests python-dotenv

# Create data directory
mkdir -p data

echo "✅ Setup complete!"
```

**This takes about 3-5 minutes.**

---

### Step 3: Upload Files from Your PC

Open a **NEW terminal/PowerShell on your PC** (keep AWS connection open in first terminal):

```bash
# Upload data file
scp D:\sfsu-cs-chatbot\data\comprehensive_sfsu_crawl.json ubuntu@YOUR_AWS_IP:~/data/

# Upload generation script
scp D:\sfsu-cs-chatbot\generate_qa_with_ollama.py ubuntu@YOUR_AWS_IP:~/
```

**Replace `YOUR_AWS_IP` with your actual IP address!**

**If using key file:**
```bash
scp -i path/to/your-key.pem D:\sfsu-cs-chatbot\data\comprehensive_sfsu_crawl.json ubuntu@YOUR_AWS_IP:~/data/
scp -i path/to/your-key.pem D:\sfsu-cs-chatbot\generate_qa_with_ollama.py ubuntu@YOUR_AWS_IP:~/
```

---

### Step 4: Run Generation on AWS

Back in your AWS terminal:

```bash
# Start generation in background (so you can close terminal)
nohup python3 generate_qa_with_ollama.py > qa_generation.log 2>&1 &

# Get the process ID
echo "Process ID: $!"

echo "✅ Generation started! Check progress with: tail -f qa_generation.log"
```

---

### Step 5: Monitor Progress

#### Option A: Watch Live Output
```bash
tail -f qa_generation.log
```
Press `Ctrl+C` to stop watching (process continues running)

#### Option B: Check Periodically
```bash
# See last 50 lines
tail -50 qa_generation.log

# Count Q&A pairs generated so far
python3 -c "import json; data=json.load(open('data/qa_training_data.json')); print(f'Generated: {len(data)} Q&A pairs')"
```

#### Option C: Auto-refresh every 30 seconds
```bash
watch -n 30 'python3 -c "import json; data=json.load(open(\"data/qa_training_data.json\")); print(f\"Q&A pairs: {len(data)}\")"'
```

---

### Step 6: You Can Disconnect Safely!

The process runs in background with `nohup`, so you can:
- ✅ Close your terminal
- ✅ Turn off your PC
- ✅ Disconnect from internet
- ✅ Come back later

**The generation will keep running on AWS!**

To check back later:
```bash
# SSH back in
ssh ubuntu@YOUR_AWS_IP

# Check if still running
ps aux | grep python3

# Check progress
tail -50 qa_generation.log
```

---

### Step 7: Download Results When Done

When generation completes (check log with `tail qa_generation.log`):

From your PC:
```bash
# Download the results
scp ubuntu@YOUR_AWS_IP:~/data/qa_training_data.json D:\sfsu-cs-chatbot\data\

# Or with key:
scp -i path/to/your-key.pem ubuntu@YOUR_AWS_IP:~/data/qa_training_data.json D:\sfsu-cs-chatbot\data\
```

---

## Expected Performance on T3

### Which T3 size do you have?

Check on AWS:
```bash
curl -s http://169.254.169.254/latest/meta-data/instance-type
```

### Performance by T3 Type:

| Instance | vCPUs | RAM | Time | Cost | Recommended |
|----------|-------|-----|------|------|-------------|
| t3.micro | 2 | 1GB | ~3-4h | $0.30 | Too slow |
| t3.small | 2 | 2GB | ~2-3h | $0.40 | Okay |
| t3.medium | 2 | 4GB | ~2h | $0.80 | Good |
| **t3.large** | **2** | **8GB** | **~90min** | **$0.20** | **✅ Best** |
| t3.xlarge | 4 | 16GB | ~60min | $0.16 | Excellent |
| t3.2xlarge | 8 | 32GB | ~45min | $0.25 | Overkill |

**Recommendation:** If you created t3.micro or t3.small, consider upgrading to **t3.large** for this task - it's actually cheaper due to faster completion!

---

## Pro Tips for T3

### 1. Use `tmux` for Better Session Management

```bash
# Install tmux
sudo apt-get update && sudo apt-get install -y tmux

# Start tmux session
tmux new -s qa_gen

# Run generation
python3 generate_qa_with_ollama.py

# Detach from session: Press Ctrl+B, then D
# Reattach later: tmux attach -t qa_gen
```

### 2. Check Progress from Your Phone/Tablet

You can SSH from phone using apps like:
- **Termius** (iOS/Android)
- **JuiceSSH** (Android)

Then run: `tail -20 qa_generation.log`

### 3. Get Notified When Done

Add this to the end of generation (on AWS):

```bash
# Add after generation completes
python3 generate_qa_with_ollama.py && \
curl -X POST https://ntfy.sh/your-topic-name \
  -d "Q&A Generation Complete! Generated $(python3 -c 'import json; data=json.load(open(\"data/qa_training_data.json\")); print(len(data))') pairs"
```

Then subscribe to https://ntfy.sh/your-topic-name on your phone

---

## Quick Copy-Paste Checklist

**On AWS EC2:**
```bash
curl -fsSL https://ollama.com/install.sh | sh && nohup ollama serve > /dev/null 2>&1 & sleep 10 && ollama pull llama3.2 && pip3 install requests python-dotenv && mkdir -p data && echo "Ready!"
```

**On Your PC:**
```bash
scp D:\sfsu-cs-chatbot\data\comprehensive_sfsu_crawl.json ubuntu@YOUR_IP:~/data/
scp D:\sfsu-cs-chatbot\generate_qa_with_ollama.py ubuntu@YOUR_IP:~/
```

**Back on AWS:**
```bash
nohup python3 generate_qa_with_ollama.py > qa_generation.log 2>&1 &
tail -f qa_generation.log
```

**When done, on PC:**
```bash
scp ubuntu@YOUR_IP:~/data/qa_training_data.json D:\sfsu-cs-chatbot\data\
```

---

## Troubleshooting

### "Connection refused"
```bash
# Restart Ollama
pkill ollama
ollama serve &
sleep 5
```

### "Out of memory"
```bash
# Check memory usage
free -h

# If low memory, use smaller model
ollama pull phi3  # Uses less RAM than llama3.2
```

### Generation seems stuck
```bash
# Check if process is running
ps aux | grep python3

# Check last activity
tail -20 qa_generation.log

# Check system resources
top
```

### Want to stop and restart
```bash
# Stop generation
pkill -f generate_qa_with_ollama.py

# Restart (will resume from checkpoint)
nohup python3 generate_qa_with_ollama.py > qa_generation.log 2>&1 &
```

---

## Summary

✅ **T3 is perfect for this task**
✅ **Cost:** $0.15-0.40 total
✅ **Time:** 45min-2hours depending on size
✅ **No PC overheating**
✅ **Can disconnect and come back**
✅ **Will process ALL 3,867 pages**

**Expected result:** ~10,000 Q&A pairs from all your data!

Ready to start? Just follow Steps 1-4 above! 🚀
