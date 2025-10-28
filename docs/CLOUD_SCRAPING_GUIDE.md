# Cloud Scraping Guide for SFSU Comprehensive Scraper

## Why Run Scraper on Cloud?

**Local machine issues:**
- ❌ Overheating during 2-8 hour scrape
- ❌ High RAM usage (10,000+ pages in memory)
- ❌ Need constant monitoring
- ❌ Risk of interruption (sleep mode, power issues)
- ❌ Slow internet connection may bottleneck

**Cloud benefits:**
- ✅ Runs 24/7 without overheating
- ✅ Scalable RAM/CPU
- ✅ Fast internet connection
- ✅ Can monitor remotely
- ✅ Automatic restarts if needed
- ✅ Cheap (free tier or $0.50-$2 for one scrape)

---

## Option 1: AWS EC2 (Free Tier) ⭐ RECOMMENDED

**Cost**: FREE (t2.micro free tier) or $0.01/hour
**Setup Time**: 10 minutes
**Best For**: One-time or occasional scrapes

### Step-by-Step Setup:

#### 1. Launch EC2 Instance

1. Go to [AWS Console](https://console.aws.amazon.com/ec2/)
2. Click "Launch Instance"
3. Choose:
   - **Name**: SFSU-Scraper
   - **OS**: Ubuntu Server 22.04 LTS (Free tier eligible)
   - **Instance type**: t2.micro (1GB RAM, free tier)
   - **Key pair**: Create new (download .pem file)
   - **Security group**: Allow SSH (port 22)
4. Click "Launch Instance"

#### 2. Connect to Instance

**Windows (using PowerShell):**
```powershell
# Set permissions on your .pem file
icacls "sfsu-scraper.pem" /inheritance:r
icacls "sfsu-scraper.pem" /grant:r "%USERNAME%:R"

# Connect via SSH
ssh -i "sfsu-scraper.pem" ubuntu@<your-ec2-public-ip>
```

**Mac/Linux:**
```bash
chmod 400 sfsu-scraper.pem
ssh -i "sfsu-scraper.pem" ubuntu@<your-ec2-public-ip>
```

#### 3. Install Python and Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3 and pip
sudo apt install python3 python3-pip python3-venv -y

# Create project directory
mkdir sfsu-scraper
cd sfsu-scraper

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install required packages
pip install requests beautifulsoup4 lxml
```

#### 4. Upload Scraper Script

**From your local machine:**
```powershell
# Upload the scraper
scp -i "sfsu-scraper.pem" scrape_comprehensive_sfsu.py ubuntu@<ec2-ip>:~/sfsu-scraper/
```

#### 5. Run Scraper in Background

```bash
# Connect to EC2
ssh -i "sfsu-scraper.pem" ubuntu@<ec2-ip>

# Navigate to project
cd sfsu-scraper
source venv/bin/activate

# Run scraper in background with nohup (continues even if you disconnect)
nohup python3 scrape_comprehensive_sfsu.py > scraper.log 2>&1 &

# Get process ID
echo $!  # Save this number!

# Check progress
tail -f scraper.log

# Disconnect safely (scraper keeps running)
# Press Ctrl+C to stop watching log, then type 'exit'
```

#### 6. Monitor Progress

```bash
# Check if still running
ps aux | grep scrape_comprehensive

# Watch log in real-time
tail -f scraper.log

# Check file size as it grows
ls -lh data/comprehensive_sfsu_crawl.json
```

#### 7. Download Results

**When scrape completes:**
```powershell
# From your local machine
scp -i "sfsu-scraper.pem" ubuntu@<ec2-ip>:~/sfsu-scraper/data/comprehensive_sfsu_crawl.json D:\sfsu-cs-chatbot\data\
```

#### 8. Terminate Instance (Stop Charges)

1. Go to EC2 Console
2. Select your instance
3. Click "Instance State" → "Terminate"

**Cost**: Free tier or ~$0.24 for 24 hours

---

## Option 2: Azure VM (Student Free Credits)

**Cost**: FREE with Azure for Students ($100 credit)
**Setup Time**: 10 minutes
**Best For**: Students with .edu email

### Step-by-Step:

#### 1. Get Azure for Students

1. Go to [Azure for Students](https://azure.microsoft.com/en-us/free/students/)
2. Sign up with your SFSU email
3. Get $100 free credit (no credit card required)

#### 2. Create VM

1. Go to [Azure Portal](https://portal.azure.com)
2. Click "Virtual Machines" → "Create"
3. Choose:
   - **Name**: sfsu-scraper
   - **Region**: West US 2
   - **Image**: Ubuntu Server 22.04 LTS
   - **Size**: B1s (1 vCPU, 1GB RAM) - cheapest
   - **Authentication**: SSH public key
4. Click "Review + Create"

#### 3. Connect and Run

```bash
# Connect (Azure provides command)
ssh azureuser@<vm-public-ip>

# Same installation steps as AWS above
# Then run scraper in background
```

**Cost**: ~$0.01/hour with student credits

---

## Option 3: Google Colab (Easiest) ⚡

**Cost**: FREE
**Setup Time**: 2 minutes
**Best For**: Quick test, no SSH needed

### Step-by-Step:

#### 1. Create Colab Notebook

1. Go to [Google Colab](https://colab.research.google.com/)
2. Click "New Notebook"

#### 2. Upload Scraper

```python
# Cell 1: Upload scraper script
from google.colab import files
uploaded = files.upload()  # Upload scrape_comprehensive_sfsu.py
```

#### 3. Install Dependencies

```python
# Cell 2: Install packages
!pip install requests beautifulsoup4 lxml
```

#### 4. Run Scraper

```python
# Cell 3: Run scraper
!python scrape_comprehensive_sfsu.py
```

#### 5. Download Results

```python
# Cell 4: Download results
from google.colab import files
files.download('data/comprehensive_sfsu_crawl.json')
```

**Limitations:**
- ⚠️ Disconnects after 12 hours
- ⚠️ May timeout if inactive
- ✅ Good for smaller scrapes (<5,000 pages)

---

## Option 4: GitHub Actions (Automated)

**Cost**: FREE (2,000 minutes/month)
**Setup Time**: 15 minutes
**Best For**: Scheduled scraping

### Setup:

Create `.github/workflows/scrape.yml`:

```yaml
name: SFSU Scraper

on:
  workflow_dispatch:  # Manual trigger
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday

jobs:
  scrape:
    runs-on: ubuntu-latest
    timeout-minutes: 360  # 6 hours max

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install requests beautifulsoup4 lxml

      - name: Run scraper
        run: |
          python scrape_comprehensive_sfsu.py

      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: scraped-data
          path: data/comprehensive_sfsu_crawl.json
```

**How to use:**
1. Push code to GitHub
2. Go to "Actions" tab
3. Click "Run workflow"
4. Download artifact when done

---

## Comparison Table

| Option | Cost | Setup Time | RAM | Duration Limit | Monitoring |
|--------|------|------------|-----|----------------|------------|
| **AWS EC2** | Free tier | 10 min | 1-8GB | Unlimited | SSH |
| **Azure VM** | $100 credit | 10 min | 1-8GB | Unlimited | SSH |
| **Google Colab** | FREE | 2 min | 12GB | 12 hours | Web UI |
| **GitHub Actions** | FREE | 15 min | 7GB | 6 hours | Web UI |

---

## My Recommendation

### For This One-Time Scrape:
**Use AWS EC2 (free tier)** - Here's why:

1. ✅ Completely free (or $0.24 for 24 hours)
2. ✅ 1GB RAM is enough for scraper
3. ✅ Can run for days if needed
4. ✅ Easy to monitor via SSH
5. ✅ Can resume if interrupted

### If You Have Azure Student Account:
**Use Azure VM** - Same setup, but you already have credits

### For Quick Test (Just CS Department):
**Use Google Colab** - Simplest, no setup needed

---

## Full Scrape Specs Needed

Based on your full scrape (10,000+ pages):

**RAM needed**: 1-2GB (scraper uses ~100MB per 1,000 pages)
**Storage needed**: 50-100MB for JSON output
**Duration**: 2-8 hours at 0.5 seconds per page
**Network**: 10-50GB data transfer (downloading HTML)

**Verdict**: t2.micro (1GB RAM) is perfect ✅

---

## Quick Start Commands

### AWS EC2:
```bash
# Launch instance → Connect → Run:
sudo apt update && sudo apt install python3-pip -y
pip3 install requests beautifulsoup4 lxml
wget https://your-github-repo/scrape_comprehensive_sfsu.py
nohup python3 scrape_comprehensive_sfsu.py > scraper.log 2>&1 &
```

### Download results later:
```bash
scp -i key.pem ubuntu@<ip>:~/data/comprehensive_sfsu_crawl.json .
```

---

## Next Steps

1. ✅ Wait for test scrape to complete (validates scraper works)
2. ✅ Check test results (CS department only)
3. ✅ Choose cloud platform (AWS recommended)
4. ✅ Deploy scraper to cloud
5. ✅ Run full scrape (all 8 domains)
6. ✅ Download results
7. ✅ Generate Q&A pairs from comprehensive data

---

## Questions?

Let me know which cloud platform you prefer, and I'll guide you through the setup!
