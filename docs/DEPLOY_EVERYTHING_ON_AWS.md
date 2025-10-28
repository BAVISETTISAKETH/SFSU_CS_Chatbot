# 🚀 Deploy Complete Stack on AWS (Frontend + Backend + Ollama)

**Host EVERYTHING on AWS - Get a professional public URL**

**What You'll Deploy**:
- ✅ Frontend (React) → AWS S3 + CloudFront
- ✅ Backend (FastAPI) → AWS EC2
- ✅ Ollama + DeepSeek R1 → AWS EC2 (same instance)
- ✅ Public URL: `https://your-cloudfront-url.cloudfront.net`

**Cost**: ~$60-120/month (depending on instance size)
**Time**: 2-3 hours
**Benefit**: 24/7 uptime, no need to keep your laptop on!

---

## 💰 AWS Cost Breakdown

### Option 1: Budget Setup (~$60/month)
- **EC2 t3.large** (2 vCPU, 8GB RAM): ~$60/month
- **S3 + CloudFront**: ~$1-5/month
- **Total**: **~$65/month**
- **Good for**: Testing, demos, small courses

### Option 2: Recommended Setup (~$120/month)
- **EC2 t3.xlarge** (4 vCPU, 16GB RAM): ~$120/month
- **S3 + CloudFront**: ~$1-5/month
- **Total**: **~$125/month**
- **Good for**: Production, 100+ users, faster responses

### Option 3: High Performance (~$250/month)
- **EC2 g4dn.xlarge** (4 vCPU, 16GB RAM, GPU): ~$250/month
- **S3 + CloudFront**: ~$1-5/month
- **Total**: **~$255/month**
- **Good for**: High traffic, fastest inference

---

## 🎯 Architecture Overview

```
AWS Cloud:
├── EC2 Instance (Ubuntu)
│   ├── Backend (FastAPI) on port 8000
│   ├── Ollama service
│   └── DeepSeek R1 model
│
├── S3 Bucket
│   └── Frontend static files (React build)
│
├── CloudFront CDN
│   └── Public URL: https://xyz.cloudfront.net
│       └── Serves frontend from S3
│
└── Security Groups
    └── Allow HTTP/HTTPS traffic
```

---

## 🚀 PART 1: Set Up EC2 Instance for Backend + Ollama

### Step 1: Create AWS Account

1. Go to https://aws.amazon.com/
2. Click "Create an AWS Account"
3. Follow signup process (need credit card)
4. **Note**: New accounts get free tier (not enough for Ollama, but other services free)

---

### Step 2: Launch EC2 Instance

1. **Go to EC2 Dashboard**:
   - https://console.aws.amazon.com/ec2/

2. **Click "Launch Instance"**

3. **Configure Instance**:

   **Name**: `sfsu-chatbot-backend`

   **Application and OS Images (AMI)**:
   - Choose: **Ubuntu Server 22.04 LTS**
   - Architecture: **64-bit (x86)**

   **Instance Type**:
   - **Budget**: `t3.large` (2 vCPU, 8GB RAM) - ~$60/month
   - **Recommended**: `t3.xlarge` (4 vCPU, 16GB RAM) - ~$120/month ⭐
   - **Performance**: `g4dn.xlarge` (4 vCPU, 16GB RAM, GPU) - ~$250/month

   **Key Pair** (Important!):
   - Click "Create new key pair"
   - Name: `sfsu-chatbot-key`
   - Type: RSA
   - Format: `.pem` (for Mac/Linux) or `.ppk` (for Windows/PuTTY)
   - Click "Create key pair"
   - **SAVE THIS FILE!** You need it to SSH into server

   **Network Settings**:
   - Click "Edit"
   - **Firewall (security groups)**: Create security group
     - Allow SSH (port 22) from "My IP"
     - Allow HTTP (port 80) from "Anywhere"
     - Allow HTTPS (port 443) from "Anywhere"
     - Allow Custom TCP (port 8000) from "Anywhere" (for backend API)

   **Configure Storage**:
   - Size: **100 GB** (need space for model)
   - Volume type: gp3 (faster, cheaper than gp2)

4. **Click "Launch Instance"**

5. **Wait 2-3 minutes** for instance to start

6. **Get Public IP**:
   - Click on your instance
   - Copy "Public IPv4 address" (e.g., `54.123.45.67`)

---

### Step 3: Connect to EC2 Instance

**On Windows** (using PowerShell):

```bash
# Change permissions on key file (first time only)
icacls "C:\Users\YourName\Downloads\sfsu-chatbot-key.pem" /inheritance:r
icacls "C:\Users\YourName\Downloads\sfsu-chatbot-key.pem" /grant:r "%username%:R"

# SSH into instance
ssh -i "C:\Users\YourName\Downloads\sfsu-chatbot-key.pem" ubuntu@YOUR_EC2_PUBLIC_IP
```

**On Mac/Linux**:

```bash
# Change permissions on key file (first time only)
chmod 400 ~/Downloads/sfsu-chatbot-key.pem

# SSH into instance
ssh -i ~/Downloads/sfsu-chatbot-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

**Type "yes"** when asked about fingerprint.

**You should now be connected to your EC2 instance!** ✅

---

### Step 4: Install Dependencies on EC2

**Update system**:
```bash
sudo apt update && sudo apt upgrade -y
```

**Install Python 3.11**:
```bash
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev python3-pip git -y
```

**Install Nginx** (web server):
```bash
sudo apt install nginx -y
```

**Install Ollama**:
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Pull DeepSeek R1 Model** (takes 5-10 minutes):
```bash
ollama pull deepseek-r1:7b

# Test it works
ollama run deepseek-r1:7b "Hello, test message"
# Press Ctrl+D to exit after you see response
```

✅ **Ollama is now running on AWS EC2!**

---

### Step 5: Deploy Backend Application

**Clone your repository**:
```bash
cd /home/ubuntu
git clone https://github.com/YOUR_USERNAME/sfsu-cs-chatbot.git
cd sfsu-cs-chatbot
```

**If you haven't pushed to GitHub yet**, use this alternative:
```bash
# On your local machine, create a zip:
# (In D:\sfsu-cs-chatbot)
# Right-click backend folder → Send to → Compressed folder

# Upload to EC2 using SCP:
scp -i "C:\Users\YourName\Downloads\sfsu-chatbot-key.pem" backend.zip ubuntu@YOUR_EC2_IP:/home/ubuntu/

# On EC2, unzip:
sudo apt install unzip -y
unzip backend.zip
```

**Set up Python environment**:
```bash
cd /home/ubuntu/sfsu-cs-chatbot/backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Create .env file**:
```bash
nano .env
```

**Paste** (replace with your actual values):
```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_DB_PASSWORD=your_db_password

# Web Search
SERPAPI_KEY=your_serpapi_key

# JWT
JWT_SECRET=your_random_32_char_string

# Email
RESEND_API_KEY=your_resend_key
SENDER_EMAIL=noreply@yourdomain.com

# Environment
ENVIRONMENT=production

# Ollama (running locally on same EC2 instance)
# No need to set - defaults to localhost:11434
```

**Save**: Ctrl+X, Y, Enter

---

### Step 6: Configure Backend as System Service

**Create systemd service**:
```bash
sudo nano /etc/systemd/system/sfsu-chatbot.service
```

**Paste**:
```ini
[Unit]
Description=SFSU Chatbot Backend API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/sfsu-cs-chatbot/backend
Environment="PATH=/home/ubuntu/sfsu-cs-chatbot/backend/venv/bin"
ExecStart=/home/ubuntu/sfsu-cs-chatbot/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Save**: Ctrl+X, Y, Enter

**Enable and start service**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable sfsu-chatbot
sudo systemctl start sfsu-chatbot

# Check status
sudo systemctl status sfsu-chatbot
```

**You should see "active (running)"** ✅

**Test backend**:
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy"}
```

---

### Step 7: Configure Nginx

**Edit Nginx config**:
```bash
sudo nano /etc/nginx/sites-available/default
```

**Replace entire file with**:
```nginx
server {
    listen 80 default_server;
    listen [::]:80 default_server;

    server_name _;

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;

        # Increase timeout for LLM responses
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://localhost:8000/health;
    }
}
```

**Save**: Ctrl+X, Y, Enter

**Test and restart Nginx**:
```bash
sudo nginx -t
sudo systemctl restart nginx
```

**Test from outside**:
```bash
# From your local machine, test:
curl http://YOUR_EC2_PUBLIC_IP/health
# Should return: {"status":"healthy"}
```

✅ **Backend is now publicly accessible!**

---

## 🚀 PART 2: Deploy Frontend to AWS S3 + CloudFront

### Step 8: Build Frontend

**On your local machine** (not EC2):

```bash
cd D:\sfsu-cs-chatbot\frontend

# Update .env to point to your EC2 backend
# Edit frontend/.env
```

**Set**:
```env
VITE_API_URL=http://YOUR_EC2_PUBLIC_IP/api
```

**Build frontend**:
```bash
npm install
npm run build
```

This creates `frontend/dist` folder with your production build.

---

### Step 9: Create S3 Bucket

1. **Go to S3 Console**:
   - https://s3.console.aws.amazon.com/s3/

2. **Click "Create bucket"**

3. **Configure**:
   - **Bucket name**: `sfsu-chatbot-frontend` (must be globally unique)
   - **Region**: Choose closest to you (e.g., `us-west-1`)
   - **Block Public Access**: UNCHECK "Block all public access"
   - ⚠️ Check "I acknowledge..." (we need public access for website)

4. **Click "Create bucket"**

---

### Step 10: Upload Frontend to S3

1. **Click on your bucket** (`sfsu-chatbot-frontend`)

2. **Click "Upload"**

3. **Add files**:
   - Navigate to `D:\sfsu-cs-chatbot\frontend\dist`
   - Select ALL files and folders inside `dist`
   - Drag and drop into S3 upload dialog

4. **Click "Upload"**

Wait for upload to complete (1-2 minutes).

---

### Step 11: Configure S3 for Static Website Hosting

1. **In your S3 bucket**, go to "Properties" tab

2. **Scroll to "Static website hosting"**

3. **Click "Edit"**

4. **Configure**:
   - **Enable**: Select "Enable"
   - **Hosting type**: Static website hosting
   - **Index document**: `index.html`
   - **Error document**: `index.html` (for React Router)

5. **Click "Save changes"**

6. **Copy the "Bucket website endpoint"**:
   - Example: `http://sfsu-chatbot-frontend.s3-website-us-west-1.amazonaws.com`

---

### Step 12: Set S3 Bucket Policy (Make Public)

1. **Go to "Permissions" tab**

2. **Scroll to "Bucket policy"**

3. **Click "Edit"**

4. **Paste this policy** (replace `YOUR-BUCKET-NAME`):

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::YOUR-BUCKET-NAME/*"
        }
    ]
}
```

5. **Click "Save changes"**

---

### Step 13: Test S3 Website

**Visit your S3 website endpoint**:
```
http://sfsu-chatbot-frontend.s3-website-us-west-1.amazonaws.com
```

You should see your chatbot! Try asking a question.

**If it works** → ✅ Backend + Frontend connected!

---

### Step 14: Create CloudFront Distribution (Optional but Recommended)

**Why CloudFront**:
- ✅ HTTPS (S3 website endpoint is HTTP only)
- ✅ Faster (CDN caching)
- ✅ Better URL
- ✅ Custom domain support

**Steps**:

1. **Go to CloudFront Console**:
   - https://console.aws.amazon.com/cloudfront/

2. **Click "Create distribution"**

3. **Configure**:
   - **Origin domain**: Select your S3 bucket from dropdown
   - **Origin access**: Select "Origin access control settings (recommended)"
   - Click "Create control setting" → Accept defaults → Create
   - **Viewer protocol policy**: Redirect HTTP to HTTPS
   - **Default root object**: `index.html`
   - **Price class**: Use all edge locations (best performance)

4. **Click "Create distribution"**

5. **Wait 5-10 minutes** for deployment

6. **Copy "Distribution domain name"**:
   - Example: `d1234567890abc.cloudfront.net`

7. **Update S3 Bucket Policy**:
   - CloudFront will prompt you to update bucket policy
   - Click "Copy policy" and update in S3 bucket permissions

---

### Step 15: Update Frontend to Use CloudFront URL

**Your CloudFront URL** is now your public website!

Example: `https://d1234567890abc.cloudfront.net`

**Update backend CORS** to allow CloudFront:

```bash
# SSH into EC2
ssh -i ~/Downloads/sfsu-chatbot-key.pem ubuntu@YOUR_EC2_IP

# Edit backend
cd /home/ubuntu/sfsu-cs-chatbot/backend
nano main.py
```

**Update CORS** (around line 39):
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        f"http://{YOUR_EC2_PUBLIC_IP}",
        "https://YOUR-CLOUDFRONT-URL.cloudfront.net",
        "*"  # Or restrict to specific domains
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Restart backend**:
```bash
sudo systemctl restart sfsu-chatbot
```

---

## ✅ You're LIVE on AWS!

**Your public URL**:
- **CloudFront**: `https://d1234567890abc.cloudfront.net` (HTTPS, fast) ⭐
- **S3**: `http://your-bucket.s3-website-region.amazonaws.com` (HTTP, slower)
- **Direct EC2**: `http://YOUR_EC2_IP` (Backend only)

**Share the CloudFront URL with professors!**

---

## 💰 Monthly Cost Summary

### With t3.xlarge (Recommended):
- **EC2 t3.xlarge**: $120/month (730 hours × $0.1664/hour)
- **EBS Storage (100GB)**: $10/month
- **S3 Storage**: <$1/month (minimal)
- **CloudFront**: $1-5/month (first 1TB free)
- **Data Transfer**: $5-10/month
- **Total**: **~$136/month**

### With t3.large (Budget):
- **EC2 t3.large**: $60/month
- **Everything else**: $15/month
- **Total**: **~$75/month**

---

## 🔧 Management Commands

### View Backend Logs:
```bash
ssh -i key.pem ubuntu@YOUR_EC2_IP
sudo journalctl -u sfsu-chatbot -f
```

### Restart Backend:
```bash
sudo systemctl restart sfsu-chatbot
```

### Restart Ollama:
```bash
sudo systemctl restart ollama
```

### Update Application:
```bash
cd /home/ubuntu/sfsu-cs-chatbot
git pull
sudo systemctl restart sfsu-chatbot
```

### Update Frontend:
```bash
# On local machine, rebuild:
cd D:\sfsu-cs-chatbot\frontend
npm run build

# Upload new dist to S3 (replace old files)
# Then invalidate CloudFront cache:
# CloudFront Console → Your distribution → Invalidations → Create invalidation → Path: /*
```

---

## 🛡️ Security Best Practices

### 1. Restrict SSH Access:
```bash
# Only allow your IP for SSH
# EC2 Console → Security Groups → Edit inbound rules
# SSH (port 22): Change from "0.0.0.0/0" to "My IP"
```

### 2. Set Up SSL/HTTPS for Backend (Optional):
- Get domain name
- Use AWS Certificate Manager (free SSL)
- Configure ALB with HTTPS

### 3. Enable AWS CloudWatch:
- Monitor EC2 metrics
- Set up alarms for high CPU/memory
- Log backend errors

---

## 🐛 Troubleshooting

### Issue: Frontend shows "Network Error"
**Check**:
1. Backend is running: `sudo systemctl status sfsu-chatbot`
2. Nginx is running: `sudo systemctl status nginx`
3. Test backend: `curl http://localhost:8000/health`
4. Check CORS settings in backend

### Issue: Ollama responses are slow
**Fix**:
- Upgrade to larger EC2 instance (t3.xlarge → g4dn.xlarge with GPU)
- Check CPU usage: `htop`

### Issue: EC2 instance out of memory
**Fix**:
- Check: `free -m`
- Upgrade instance type
- Or reduce model size (use 3B instead of 7B)

### Issue: CloudFront showing old content
**Fix**:
- Create invalidation: `/*` path
- Wait 2-3 minutes

---

## 📊 Monitoring Your AWS Deployment

### CloudWatch Dashboard:
1. Go to CloudWatch console
2. View EC2 metrics:
   - CPU Utilization
   - Network In/Out
   - Disk I/O

### Cost Explorer:
1. Go to AWS Cost Explorer
2. View daily costs
3. Set budget alerts

### Set Budget Alert:
1. Go to AWS Budgets
2. Create budget: $150/month
3. Get email if exceeded

---

## 🎯 Custom Domain (Optional)

### If you have a domain (e.g., sfsu-chatbot.com):

1. **Route 53** (AWS DNS):
   - Buy domain or transfer existing
   - Create hosted zone

2. **Certificate Manager**:
   - Request SSL certificate
   - Add CNAME records for validation

3. **CloudFront**:
   - Add alternate domain name
   - Select SSL certificate

4. **Route 53**:
   - Create A record → Alias to CloudFront

**Result**: `https://sfsu-chatbot.com` instead of CloudFront URL

---

## ✅ Final Checklist

- [ ] EC2 instance running
- [ ] Ollama working: `ollama list`
- [ ] Backend running: `sudo systemctl status sfsu-chatbot`
- [ ] Nginx configured
- [ ] S3 bucket created and public
- [ ] Frontend uploaded to S3
- [ ] CloudFront distribution created
- [ ] CORS updated in backend
- [ ] SQL migrations run in Supabase
- [ ] Can access via CloudFront URL
- [ ] Can ask questions and get responses
- [ ] All features work (flag, notifications, etc.)

---

## 🎉 You're Done!

**What you have now**:
- ✅ 24/7 uptime (no laptop needed!)
- ✅ Professional public URL
- ✅ HTTPS enabled
- ✅ Fast CDN delivery
- ✅ Ollama running on AWS
- ✅ Full control
- ✅ NO rate limits

**Share your URL**:
```
https://YOUR-CLOUDFRONT-URL.cloudfront.net
```

**Cost**: ~$75-136/month depending on instance type

---

## 🔄 Cheaper Alternatives to Consider

If $75-136/month is too much:

1. **AWS Lightsail**: $40-80/month (simpler than EC2)
2. **Hetzner VPS**: $12/month (but not AWS)
3. **Groq API**: FREE (but has rate limits)
4. **Keep laptop running + Cloudflare Tunnel**: FREE (but not 24/7)

---

**Need help?** All AWS services have detailed documentation and support forums!

**Ready to deploy?** Follow the steps above! 🚀
