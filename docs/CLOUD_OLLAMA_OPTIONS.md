# Running Ollama on Cloud (Avoid PC Overheating)

## Cloud Options for Ollama

### Option 1: Runpod.io ⭐ CHEAPEST & EASIEST

**Cost:** ~$0.30-0.50 for entire job (30-90 minutes)

**Setup:**
1. Create account: https://runpod.io
2. Deploy "Ollama" template
3. Select GPU: RTX 3060 (~$0.30/hour)
4. Upload your script + data
5. Run generation
6. Download results

**Advantages:**
- ✅ Very cheap (pay per minute)
- ✅ Fast setup (5 minutes)
- ✅ GPU accelerated
- ✅ No PC load/heat

**Total Cost:** ~$0.50 for all 3,867 pages

---

### Option 2: Google Colab FREE

**Cost:** FREE (with limits)

**Setup:**
1. Go to: https://colab.research.google.com
2. Create new notebook
3. Install Ollama
4. Upload your data
5. Run script

**Notebook Code:**
```python
# Install Ollama
!curl -fsSL https://ollama.com/install.sh | sh
!ollama serve &
!sleep 5
!ollama pull llama3.2

# Upload your files via Colab UI
# Then run generation script
!python generate_qa_with_ollama.py
```

**Advantages:**
- ✅ FREE
- ✅ No PC load
- ✅ GPU included (T4)
- ⚠️ Session limits (12 hours max)

---

### Option 3: AWS EC2 / Azure / GCP

**Cost:** ~$1-3 for entire job

**Best for:** If you already have cloud credits

**Setup:**
1. Launch GPU instance (e.g., g4dn.xlarge on AWS)
2. Install Ollama
3. Run generation
4. Terminate instance

---

### Option 4: Modal.com ⭐ EASIEST SETUP

**Cost:** $0.50-1 for entire job

**Setup:**
```bash
pip install modal

# Create modal_qa_generation.py
modal deploy modal_qa_generation.py
```

**Advantages:**
- ✅ Serverless (auto-scale)
- ✅ Easy deployment
- ✅ Pay only for compute time
- ✅ No instance management

---

## Local Options (If You Want to Use Your PC)

### Prevent Overheating on Your PC

#### 1. **Limit CPU/GPU Usage**

Update `generate_qa_with_ollama.py`:

```python
# Limit to 50% CPU to reduce heat
payload = {
    "model": model,
    "prompt": prompt,
    "stream": False,
    "options": {
        "temperature": 0.7,
        "num_predict": 1500,
        "num_thread": 4,  # Limit threads (adjust based on your CPU)
        "num_gpu": 0.5,   # Use only 50% GPU
    }
}
```

#### 2. **Run During Cooler Times**
- Run at night when ambient temperature is lower
- Improve room ventilation

#### 3. **Process in Batches**
```python
# Process 500 pages at a time
python generate_qa_with_ollama.py  # Edit max_pages=500
# Wait 30 min, let PC cool
python generate_qa_with_ollama.py  # Resume from checkpoint
```

---

## Cost Comparison

| Method | Cost | Time | PC Load | Setup |
|--------|------|------|---------|-------|
| **Local PC** | FREE | 30-90 min | HIGH 🔥 | 5 min |
| **Runpod GPU** | ~$0.50 | 20 min | NONE | 10 min |
| **Google Colab** | FREE | 60 min | NONE | 15 min |
| **Modal.com** | ~$0.80 | 30 min | NONE | 20 min |
| **AWS/Azure** | ~$1-3 | 30 min | NONE | 30 min |

---

## Recommendation for You

### For Avoiding PC Overheating:

**Best: Runpod.io** ($0.50, 20 minutes)
- Cheapest cloud option
- Fast GPU
- Easy setup
- Pay only for what you use

**Alternative: Google Colab** (FREE, 60 minutes)
- Completely free
- Good GPU (T4)
- Easy to use
- Session limits (but 60 min is enough)

---

## Quick Setup: Google Colab (FREE)

I'll create a ready-to-use Colab notebook for you:

### Steps:
1. Go to: https://colab.research.google.com
2. Create new notebook
3. Copy this code:

```python
# Cell 1: Install Ollama
!curl -fsSL https://ollama.com/install.sh | sh
!nohup ollama serve &
!sleep 10
!ollama pull llama3.2
print("✅ Ollama ready!")

# Cell 2: Install dependencies
!pip install python-dotenv requests

# Cell 3: Upload files
# Use Colab's file upload UI to upload:
# - generate_qa_with_ollama.py
# - data/comprehensive_sfsu_crawl.json

# Cell 4: Run generation
!python generate_qa_with_ollama.py

# Cell 5: Download results
from google.colab import files
files.download('data/qa_training_data.json')
```

4. Run cells in order
5. Download results when done

**Total time:** ~60 minutes
**Cost:** FREE
**PC load:** ZERO

---

## For Runpod (Cheapest Paid Option)

### Setup:
1. Sign up: https://runpod.io
2. Add $5 credit (will use ~$0.50)
3. Click "Deploy" → Search "Ollama"
4. Select GPU: RTX 3060 ($0.30/hour)
5. Start pod
6. Upload your files via web interface
7. Run in terminal:
```bash
ollama pull llama3.2
python generate_qa_with_ollama.py
```
8. Download `data/qa_training_data.json`
9. Stop pod (important!)

**Total cost:** ~$0.50
**Time:** ~20 minutes (GPU is fast!)
**PC load:** ZERO

---

## Summary

**Yes! You can definitely run on cloud to avoid PC overheating.**

**Recommendations:**
1. **FREE option:** Google Colab (60 min, no PC load)
2. **Paid option:** Runpod ($0.50, fastest, no PC load)
3. **Local (if must):** Process in batches, run at night, limit CPU/GPU usage

Would you like me to create a ready-to-use Colab notebook for you?
