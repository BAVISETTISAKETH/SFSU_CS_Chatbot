# 🎓 Complete Guide: Deploy with GitHub Student Pack (DigitalOcean)

**What You're Deploying**:
- ✅ Backend (FastAPI) + Ollama + DeepSeek R1
- ✅ Frontend (React)
- ✅ Public URL: `http://YOUR_DROPLET_IP`

**Cost**: FREE for 8-12 months (with $200 credit)
**Time**: 1-2 hours
**Difficulty**: ⭐⭐ Easy

---

## 🎯 What You'll Get

```
DigitalOcean Droplet:
├── Ubuntu 22.04
├── 4 vCPU, 8GB RAM
├── 160GB Storage
├── Backend (FastAPI)
├── Ollama + DeepSeek R1 7B
├── Frontend (Nginx)
└── Public IP: http://YOUR_IP
```

**Result**: Professional chatbot with public URL! 🚀

---

## 📋 PART 1: Get GitHub Student Developer Pack

### Step 1: Sign Up for GitHub Student Pack

**Time**: 5-15 minutes (instant with .edu email, or 1-3 days with student ID)

1. **Go to**: https://education.github.com/pack

2. **Click**: "Sign up for Student Developer Pack"

3. **Sign in** to your GitHub account (or create one)

4. **Fill out the form**:

   **How do you plan to use GitHub?**
   - Select: "For school/university projects"

   **What school do you attend?**
   - Type your school name: "San Francisco State University"
   - Select from dropdown

   **How do you plan to use GitHub?**
   - Write something like: "Building an AI chatbot for CS department as a class project"

5. **Choose Verification Method**:

   **Option A: School-issued email (FASTEST - Instant)**
   - If you have .edu email
   - Click "Continue"
   - Check your .edu email for verification link
   - Click link → **APPROVED INSTANTLY!** ✅

   **Option B: Upload proof (Takes 1-3 days)**
   - If no .edu email
   - Upload:
     - Student ID (photo)
     - OR Official enrollment letter
     - OR Transcript
   - Click "Submit"
   - Wait for approval email (usually 1-3 days)

6. **Wait for approval**:
   - With .edu email: Instant! ✅
   - With document: 1-3 business days

7. **Check approval status**:
   - Go to https://education.github.com/pack
   - Should see: "You have access to the GitHub Student Developer Pack" ✅

---

### Step 2: Access DigitalOcean Credit

1. **Go to your Student Pack**: https://education.github.com/pack

2. **Scroll down** to find "DigitalOcean"

3. **Click**: "Get access by connecting your GitHub account"

4. **You'll be redirected** to DigitalOcean

5. **Click**: "Authorize DigitalOcean"

6. **Create DigitalOcean account**:
   - Fill in your details
   - **Email**: Use your regular email (doesn't need to be .edu)
   - **Password**: Create strong password

7. **Verify email**:
   - Check your email
   - Click verification link

8. **Add payment method**:
   - Even though you have $200 credit, DigitalOcean requires payment method on file
   - Add credit/debit card
   - **Don't worry**: Won't be charged while you have credit!
   - Your $200 credit will be used first

9. **Verify credit is applied**:
   - Go to https://cloud.digitalocean.com/
   - Click "Billing" in left menu
   - Should see: **"$200.00 Promotional Credit"** ✅
   - Valid for 1 year

✅ **You now have $200 DigitalOcean credit!**

---

## 📋 PART 2: Create Droplet (Server)

### Step 3: Create Your Droplet

**Time**: 5 minutes

1. **Go to**: https://cloud.digitalocean.com/

2. **Click**: "Create" (top right) → "Droplets"

3. **Choose Region**:
   - Select closest to you: **San Francisco 3** (for SF Bay Area)
   - Or: New York, Toronto, London, etc.

4. **Choose Image**:
   - Click: **"Ubuntu"**
   - Select: **"Ubuntu 22.04 (LTS) x64"** ✅

5. **Choose Size**:

   **Droplet Type**: Select **"Regular Intel with SSD"**

   **CPU Options**:
   - Click the **"8 GB / 4 CPUs"** option
   - Cost: **$48/month** (but FREE with your credit!)
   - Specs: 4 vCPU, 8GB RAM, 160GB SSD
   - **This will last ~4 months with your $200 credit**

   **OR** if you want to make credit last longer:
   - Click the **"4 GB / 2 CPUs"** option
   - Cost: **$24/month**
   - Specs: 2 vCPU, 4GB RAM, 80GB SSD
   - **This will last ~8 months with your $200 credit**
   - ⚠️ Might be slower with Ollama

   **I recommend**: 8 GB / 4 CPUs ($48/month) for better performance ⭐

6. **Choose Authentication**:

   Select: **"SSH Keys"** (more secure)

   **Create SSH Key** (if you don't have one):

   **On Windows**:
   ```bash
   # Open PowerShell and run:
   ssh-keygen -t rsa -b 4096

   # Press Enter for default location
   # Press Enter twice for no passphrase (or set one if you want)

   # View your public key:
   type C:\Users\YOUR_USERNAME\.ssh\id_rsa.pub

   # Copy the entire output (starts with "ssh-rsa ...")
   ```

   **On Mac/Linux**:
   ```bash
   # Open Terminal and run:
   ssh-keygen -t rsa -b 4096

   # Press Enter for default location
   # Press Enter twice for no passphrase

   # View your public key:
   cat ~/.ssh/id_rsa.pub

   # Copy the entire output
   ```

   **Back in DigitalOcean**:
   - Click "New SSH Key"
   - Paste your public key
   - Name it: "My Laptop"
   - Click "Add SSH Key"

7. **Finalize Details**:

   **How many Droplets?**: 1

   **Choose a hostname**: `sfsu-chatbot`

   **Tags**: (optional, leave blank)

   **Project**: Leave as "first-project"

   **Backups**: (optional) You can enable weekly backups for extra $9.60/month

8. **Click**: "Create Droplet"

9. **Wait 30-60 seconds** for droplet creation

10. **Copy your Droplet's IP address**:
    - You'll see something like: `164.92.123.456`
    - **Copy this IP** - you'll need it! 📋

✅ **Droplet created!**

---

## 📋 PART 3: Connect to Your Droplet

### Step 4: SSH into Droplet

**On Windows** (PowerShell):
```bash
ssh root@YOUR_DROPLET_IP
```

**On Mac/Linux** (Terminal):
```bash
ssh root@YOUR_DROPLET_IP
```

Replace `YOUR_DROPLET_IP` with the IP you copied (e.g., `164.92.123.456`)

**First time connecting**:
- You'll see: "The authenticity of host... are you sure?"
- Type: `yes` and press Enter

**You should see**:
```
Welcome to Ubuntu 22.04.3 LTS
...
root@sfsu-chatbot:~#
```

✅ **You're connected!**

---

## 📋 PART 4: Install Everything

### Step 5: Update System

```bash
apt update && apt upgrade -y
```

**This takes 5-10 minutes**. Wait for it to complete.

---

### Step 6: Install Python 3.11

```bash
# Add Python repository
apt install software-properties-common -y
add-apt-repository ppa:deadsnakes/ppa -y
apt update

# Install Python 3.11
apt install python3.11 python3.11-venv python3.11-dev python3-pip -y

# Verify installation
python3.11 --version
```

**You should see**: `Python 3.11.x` ✅

---

### Step 7: Install Node.js 20

```bash
# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install nodejs -y

# Verify
node --version
npm --version
```

**You should see**:
- `v20.x.x`
- `10.x.x`

✅ Done!

---

### Step 8: Install Nginx

```bash
apt install nginx -y

# Start Nginx
systemctl start nginx
systemctl enable nginx

# Check status
systemctl status nginx
```

**You should see**: "active (running)" ✅

**Test it**:
- Open browser
- Go to: `http://YOUR_DROPLET_IP`
- Should see: "Welcome to nginx!" page

---

### Step 9: Install Ollama

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Verify it's running
systemctl status ollama
```

**You should see**: "active (running)" ✅

---

### Step 10: Pull DeepSeek R1 Model

**This takes 5-10 minutes** - downloading ~4GB model:

```bash
# Pull the model
ollama pull deepseek-r1:7b

# Wait for download...
# You'll see progress: [==============>      ] 60%

# Test it works
ollama run deepseek-r1:7b "Hello, this is a test"
```

**You should see a response!** ✅

Press `Ctrl+D` to exit.

---

## 📋 PART 5: Deploy Your Application

### Step 11: Upload Your Code

**Option A: If code is on GitHub**:

```bash
cd /root
git clone https://github.com/YOUR_USERNAME/sfsu-cs-chatbot.git
cd sfsu-cs-chatbot
```

**Option B: Upload from your local machine**:

**On your local machine** (in D:\sfsu-cs-chatbot):

**Windows PowerShell**:
```bash
# Create zip files
Compress-Archive -Path backend -DestinationPath backend.zip
Compress-Archive -Path frontend -DestinationPath frontend.zip

# Upload to DigitalOcean
scp backend.zip root@YOUR_DROPLET_IP:/root/
scp frontend.zip root@YOUR_DROPLET_IP:/root/
```

**Mac/Linux**:
```bash
# Create tar files
tar -czf backend.tar.gz backend
tar -czf frontend.tar.gz frontend

# Upload to DigitalOcean
scp backend.tar.gz root@YOUR_DROPLET_IP:/root/
scp frontend.tar.gz root@YOUR_DROPLET_IP:/root/
```

**Then on the Droplet**:

```bash
cd /root

# Extract files
unzip backend.zip  # If Windows
unzip frontend.zip

# OR
tar -xzf backend.tar.gz  # If Mac/Linux
tar -xzf frontend.tar.gz

# Create project directory
mkdir -p sfsu-cs-chatbot
mv backend sfsu-cs-chatbot/
mv frontend sfsu-cs-chatbot/
cd sfsu-cs-chatbot
```

---

### Step 12: Set Up Backend

```bash
cd /root/sfsu-cs-chatbot/backend

# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies (takes 5-10 minutes)
pip install -r requirements.txt
```

**Wait for all packages to install**...

---

### Step 13: Configure Backend Environment

```bash
# Create .env file
nano .env
```

**Paste this** (replace with YOUR actual values):

```env
# Supabase (get from https://supabase.com/dashboard)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_DB_PASSWORD=your_database_password

# SerpAPI (get from https://serpapi.com/)
SERPAPI_KEY=your_serpapi_key

# JWT Secret (generate random string)
JWT_SECRET=your_random_32_character_secret_key_here_make_it_long

# Resend (get from https://resend.com/)
RESEND_API_KEY=your_resend_api_key
SENDER_EMAIL=noreply@yourdomain.com

# Environment
ENVIRONMENT=production

# Ollama (running locally - no config needed)
# Defaults to http://localhost:11434
```

**Save**:
- Press `Ctrl+X`
- Press `Y`
- Press `Enter`

---

### Step 14: Test Backend

```bash
# Make sure you're in backend directory with venv activated
cd /root/sfsu-cs-chatbot/backend
source venv/bin/activate

# Run backend
python main.py
```

**You should see**:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Test in another terminal** (open new SSH connection):

```bash
curl http://localhost:8000/health
```

**Should return**: `{"status":"healthy"}` ✅

Press `Ctrl+C` in first terminal to stop backend.

---

### Step 15: Create Backend Service

```bash
nano /etc/systemd/system/sfsu-chatbot.service
```

**Paste**:

```ini
[Unit]
Description=SFSU Chatbot Backend
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/sfsu-cs-chatbot/backend
Environment="PATH=/root/sfsu-cs-chatbot/backend/venv/bin"
ExecStart=/root/sfsu-cs-chatbot/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Save**: `Ctrl+X`, `Y`, `Enter`

**Start the service**:

```bash
# Reload systemd
systemctl daemon-reload

# Enable service (start on boot)
systemctl enable sfsu-chatbot

# Start service
systemctl start sfsu-chatbot

# Check status
systemctl status sfsu-chatbot
```

**You should see**: "active (running)" in green ✅

---

## 📋 PART 6: Deploy Frontend

### Step 16: Build Frontend

```bash
cd /root/sfsu-cs-chatbot/frontend

# Create .env
nano .env
```

**Paste**:
```env
VITE_API_URL=/api
```

**Save**: `Ctrl+X`, `Y`, `Enter`

**Build frontend**:

```bash
# Install dependencies (takes 2-3 minutes)
npm install

# Build for production (takes 1-2 minutes)
npm run build

# Check build was created
ls dist
```

**You should see**: `index.html`, `assets`, etc. ✅

---

## 📋 PART 7: Configure Nginx

### Step 17: Configure Nginx

```bash
nano /etc/nginx/sites-available/default
```

**Delete everything and paste**:

```nginx
server {
    listen 80 default_server;
    listen [::]:80 default_server;

    server_name _;

    root /root/sfsu-cs-chatbot/frontend/dist;
    index index.html;

    # Frontend - Serve React app
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Backend API - Proxy to FastAPI
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

    # Health check
    location /health {
        proxy_pass http://localhost:8000/health;
    }
}
```

**Save**: `Ctrl+X`, `Y`, `Enter`

**Test and restart Nginx**:

```bash
# Test configuration
nginx -t

# Should say: "test is successful"

# Restart Nginx
systemctl restart nginx

# Check status
systemctl status nginx
```

**Should show**: "active (running)" ✅

---

## 📋 PART 8: Configure Firewall

### Step 18: Set Up UFW Firewall

```bash
# Install UFW (if not installed)
apt install ufw -y

# Allow SSH (IMPORTANT - don't lock yourself out!)
ufw allow 22/tcp

# Allow HTTP
ufw allow 80/tcp

# Allow HTTPS
ufw allow 443/tcp

# Enable firewall
ufw --force enable

# Check status
ufw status
```

**You should see**:
```
Status: active

To                         Action      From
--                         ------      ----
22/tcp                     ALLOW       Anywhere
80/tcp                     ALLOW       Anywhere
443/tcp                    ALLOW       Anywhere
```

✅ Done!

---

## 📋 PART 9: Run Database Migrations

### Step 19: Run SQL in Supabase

**Don't forget the database migrations!**

1. Go to: https://supabase.com/dashboard
2. Open your project
3. Click: **SQL Editor** → **New query**

**Run Migration 1**:
```sql
-- Add session_id to corrections table
ALTER TABLE corrections
ADD COLUMN IF NOT EXISTS session_id VARCHAR(100);

CREATE INDEX IF NOT EXISTS corrections_session_id_idx ON corrections(session_id);
```

Click **Run** ✅

**Run Migration 2**:
```sql
-- Create notifications table
CREATE TABLE IF NOT EXISTS notifications (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,
    correction_id BIGINT REFERENCES corrections(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR(50) NOT NULL CHECK (type IN ('correction_approved', 'correction_rejected', 'correction_edited')),
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS notifications_session_id_idx ON notifications(session_id);
CREATE INDEX IF NOT EXISTS notifications_is_read_idx ON notifications(is_read);
CREATE INDEX IF NOT EXISTS notifications_created_at_idx ON notifications(created_at DESC);
```

Click **Run** ✅

---

## 🎉 YOU'RE LIVE!

### Step 20: Test Your Chatbot!

**Visit**: `http://YOUR_DROPLET_IP`

Example: `http://164.92.123.456`

**You should see your chatbot!** 🎉

**Test everything**:
1. ✅ Ask a question: "What is CS 101?"
2. ✅ Get a response (should work!)
3. ✅ Verify no [Local]/[Web] tags
4. ✅ Test flag incorrect
5. ✅ Test professor login
6. ✅ Test notifications
7. ✅ Test view corrections

---

## 🔗 Share Your Link!

**Your public URL**: `http://YOUR_DROPLET_IP`

**Share with**:
- Professors for review ✅
- Classmates for testing ✅
- Anyone with internet! ✅

---

## 🛠️ Management Commands

### View Backend Logs:
```bash
journalctl -u sfsu-chatbot -f
```

### Restart Backend:
```bash
systemctl restart sfsu-chatbot
```

### Check Backend Status:
```bash
systemctl status sfsu-chatbot
```

### Restart Ollama:
```bash
systemctl restart ollama
```

### Check Ollama:
```bash
ollama list
ollama ps
```

### Restart Nginx:
```bash
systemctl restart nginx
```

### Check All Services:
```bash
systemctl status sfsu-chatbot
systemctl status ollama
systemctl status nginx
```

---

## 🔄 Update Your Application

### Update Backend Code:

**If using GitHub**:
```bash
cd /root/sfsu-cs-chatbot
git pull
systemctl restart sfsu-chatbot
```

**If uploading manually**:
```bash
# On local machine, upload new files
scp -r D:\sfsu-cs-chatbot\backend root@YOUR_IP:/root/sfsu-cs-chatbot/

# On droplet, restart
systemctl restart sfsu-chatbot
```

### Update Frontend:

```bash
cd /root/sfsu-cs-chatbot/frontend
npm run build
systemctl restart nginx
```

---

## 📊 Monitor Your Usage & Credit

### Check Remaining Credit:

1. Go to: https://cloud.digitalocean.com/
2. Click "Billing" in left menu
3. See "Promotional Credit" balance
4. See "Month-to-Date Usage"

**With $48/month droplet**: ~4 months free
**With $24/month droplet**: ~8 months free

---

## 🐛 Troubleshooting

### Issue: Can't SSH into droplet

**Check**:
1. Using correct IP address
2. SSH key is set up correctly
3. DigitalOcean firewall allows SSH (port 22)

**Fix**:
```bash
# Make sure SSH key has correct permissions
# Windows: Already handled
# Mac/Linux:
chmod 600 ~/.ssh/id_rsa
```

---

### Issue: Can't access website (Connection refused)

**Check**:
1. Backend is running: `systemctl status sfsu-chatbot`
2. Nginx is running: `systemctl status nginx`
3. Firewall allows port 80: `ufw status`

**Fix**:
```bash
# Restart services
systemctl restart sfsu-chatbot
systemctl restart nginx

# Check firewall
ufw allow 80/tcp
ufw reload
```

---

### Issue: Frontend loads but "Network Error"

**Check**:
1. Backend is running: `curl http://localhost:8000/health`
2. Check backend logs: `journalctl -u sfsu-chatbot -f`

**Fix**:
```bash
# Check backend logs
journalctl -u sfsu-chatbot -n 50

# Restart backend
systemctl restart sfsu-chatbot
```

---

### Issue: Ollama not responding

**Check**:
```bash
systemctl status ollama
ollama ps
```

**Fix**:
```bash
# Restart Ollama
systemctl restart ollama

# Reload model
ollama run deepseek-r1:7b "test"
# Press Ctrl+D
```

---

### Issue: Out of disk space

**Check**:
```bash
df -h
```

**Fix**:
```bash
# Clean old logs
journalctl --vacuum-time=7d

# Clean apt cache
apt clean
apt autoremove -y
```

---

## 💰 When Credit Runs Out (8-12 months)

### Option 1: Pay for DigitalOcean
- Continue using DigitalOcean
- $24-48/month depending on your droplet size

### Option 2: Migrate to Oracle Cloud (FREE Forever)
- Follow: `DEPLOY_ORACLE_CLOUD_COMPLETE.md`
- Backup your data first
- Deploy to Oracle
- Update DNS/URLs
- **Cost**: $0 forever!

### Option 3: Switch to Groq API
- No more Ollama needed
- Follow: `DEPLOY_NOW.md`
- Change 1 line of code
- Deploy to Vercel + Railway
- **Cost**: $0 (with rate limits)

**I recommend**: Migrate to Oracle Cloud for FREE forever! ✅

---

## ✅ Success Checklist

- [ ] GitHub Student Pack approved
- [ ] $200 DigitalOcean credit applied
- [ ] Droplet created (4 vCPU, 8GB RAM)
- [ ] SSH access working
- [ ] Python 3.11 installed
- [ ] Node.js installed
- [ ] Nginx installed
- [ ] Ollama installed
- [ ] DeepSeek R1 model downloaded
- [ ] Backend deployed and running
- [ ] Frontend built and deployed
- [ ] Nginx configured
- [ ] Firewall configured
- [ ] SQL migrations run in Supabase
- [ ] Can access via http://YOUR_IP
- [ ] Chat works
- [ ] All features tested
- [ ] Link shared with professor

---

## 🎉 Congratulations!

You now have:
- ✅ **Professional chatbot** with public URL
- ✅ **Ollama + DeepSeek R1** running in cloud
- ✅ **FREE for 8-12 months** (with $200 credit)
- ✅ **24/7 uptime** (no laptop needed!)
- ✅ **Easy to manage** (DigitalOcean UI is great)
- ✅ **Full control**

**Your URL**: `http://YOUR_DROPLET_IP`

**Share it with**:
- Professors ✅
- Students ✅
- Anyone! ✅

---

## 📞 Need Help?

**DigitalOcean Resources**:
- Docs: https://docs.digitalocean.com/
- Community: https://www.digitalocean.com/community/
- Tutorials: https://www.digitalocean.com/community/tutorials

**Check logs first**:
```bash
journalctl -u sfsu-chatbot -f    # Backend logs
journalctl -u ollama -f          # Ollama logs
tail -f /var/log/nginx/error.log # Nginx errors
```

---

**TIME**: 1-2 hours
**COST**: FREE for 8-12 months
**RESULT**: Professional 24/7 chatbot! 🚀

**You're LIVE on DigitalOcean!** 🎉
