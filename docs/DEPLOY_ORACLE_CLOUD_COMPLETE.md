# 🚀 Deploy to Oracle Cloud - Complete Guide (Ollama + DeepSeek R1)

**What You're Deploying**:
- ✅ Backend (FastAPI)
- ✅ Ollama + DeepSeek R1 7B
- ✅ Frontend (React)
- ✅ Public URL for sharing

**Cost**: $0 (FREE FOREVER)
**Time**: 2-3 hours
**Your Code**: NO changes needed!

---

## 🎯 What You'll Get

```
Oracle Cloud (FREE):
├── Compute Instance (Ampere A1)
│   ├── 4 vCPU (ARM)
│   ├── 24GB RAM
│   ├── 100GB Storage
│   ├── Backend (FastAPI) on port 8000
│   ├── Ollama service
│   ├── DeepSeek R1 7B model
│   └── Frontend (Nginx)
└── Public IP → http://YOUR_ORACLE_IP
```

**Result**: Professional public URL, 24/7 uptime, $0 cost! ✅

---

## 📋 Part 1: Create Oracle Cloud Account

### Step 1: Sign Up

1. **Go to**: https://www.oracle.com/cloud/free/

2. **Click**: "Start for free"

3. **Fill out form**:
   - **Country**: Select your country
   - **Name**: Your name
   - **Email**: Your email (can use Gmail)
   - **Password**: Create strong password

4. **Click**: "Verify my email"

5. **Check email** and click verification link

---

### Step 2: Complete Account Setup

1. **Account Information**:
   - **Cloud Account Name**: Choose unique name (e.g., `sfsu-chatbot-123`)
   - **Home Region**: Choose closest to you (e.g., US West - San Jose)
   - ⚠️ **Important**: Cannot change region later!

2. **Address Information**:
   - Fill in your address

3. **Payment Verification**:
   - Enter credit card details
   - ⚠️ This is for verification ONLY
   - ⚠️ You will NOT be charged if you stay in "Always Free" tier
   - Oracle charges $1 for verification (refunded immediately)

4. **Phone Verification**:
   - Enter phone number
   - Enter verification code sent via SMS

5. **Review and Accept**:
   - Read terms and conditions
   - Check "I have reviewed and accept..."
   - Click "Start my free trial"

6. **Wait 2-3 minutes** for account provisioning

7. **You'll see**: "Your Cloud Account is Ready!"

---

## 📋 Part 2: Create Compute Instance

### Step 3: Access Oracle Cloud Console

1. **Sign in** at: https://cloud.oracle.com/

2. **Enter**:
   - **Cloud Account Name**: (what you chose earlier)
   - Click "Next"
   - **Username**: Your email
   - **Password**: Your password

3. **You're in!** You should see the Oracle Cloud dashboard

---

### Step 4: Create Compute Instance

1. **Click** the hamburger menu (≡) in top-left

2. **Navigate**: Compute → Instances

3. **Click**: "Create Instance"

4. **Configure Instance**:

   **Name**: `sfsu-chatbot`

   **Placement**:
   - **Availability domain**: Leave default
   - **Fault domain**: Leave default

   **Image and Shape**:
   - **Image**: Should show "Oracle Linux 8"
   - Click "Change Image"
   - Select: **Canonical Ubuntu 22.04**
   - Click "Select Image"

   **Shape**:
   - Click "Change Shape"
   - **Instance type**: Select "Virtual machine"
   - **Shape series**: Select "Ampere"
   - **Shape**: Select "VM.Standard.A1.Flex"
   - **Number of OCPUs**: Move slider to **4**
   - **Amount of memory (GB)**: Should auto-adjust to **24GB**
   - ✅ **This is the Always Free eligible shape!**
   - Click "Select Shape"

   **Networking**:
   - **Virtual Cloud Network**: Select "Create new virtual cloud network"
   - **Subnet**: Select "Create new public subnet"
   - **Public IPv4 address**: Make sure "Assign a public IPv4 address" is CHECKED ✅
   - Leave other defaults

   **Add SSH Keys**:
   - Select: "Generate a key pair for me"
   - Click "Save Private Key" - **IMPORTANT! Save this file!**
   - File will be named something like `ssh-key-2025-01-27.key`
   - **Save to safe location** (e.g., Downloads folder)
   - Click "Save Public Key" (optional but recommended)

   **Boot Volume**:
   - **Size (GB)**: Change to **100 GB** (need space for model)
   - Leave other defaults

5. **Click**: "Create"

6. **Wait 2-3 minutes** for instance to provision

7. **Instance status** will change from "Provisioning" → "Running" (orange → green)

8. **Copy Public IP Address**:
   - You'll see "Public IP address: 123.45.67.89"
   - **Copy this IP** - you'll need it!

---

### Step 5: Configure Firewall (Security List)

**Important**: Oracle blocks all ports by default. We need to open them!

1. **On the instance page**, scroll down to "Primary VNIC"

2. **Click**: on the subnet name (looks like "subnet-20250127...")

3. **Under "Security Lists"**, click on the security list (looks like "Default Security List...")

4. **Click**: "Add Ingress Rules"

5. **Add Rule 1 - SSH**:
   - **Source CIDR**: `0.0.0.0/0`
   - **IP Protocol**: TCP
   - **Source Port Range**: (leave blank)
   - **Destination Port Range**: `22`
   - **Description**: SSH access
   - Click "Add Ingress Rules"

6. **Click**: "Add Ingress Rules" again

7. **Add Rule 2 - HTTP**:
   - **Source CIDR**: `0.0.0.0/0`
   - **IP Protocol**: TCP
   - **Destination Port Range**: `80`
   - **Description**: HTTP
   - Click "Add Ingress Rules"

8. **Click**: "Add Ingress Rules" again

9. **Add Rule 3 - HTTPS**:
   - **Source CIDR**: `0.0.0.0/0`
   - **IP Protocol**: TCP
   - **Destination Port Range**: `443`
   - **Description**: HTTPS
   - Click "Add Ingress Rules"

10. **Click**: "Add Ingress Rules" again

11. **Add Rule 4 - Backend API**:
    - **Source CIDR**: `0.0.0.0/0`
    - **IP Protocol**: TCP
    - **Destination Port Range**: `8000`
    - **Description**: Backend API
    - Click "Add Ingress Rules"

✅ **Firewall configured!**

---

## 📋 Part 3: Connect to Instance

### Step 6: Connect via SSH

**On Windows** (using PowerShell):

```bash
# Navigate to where you saved the SSH key
cd C:\Users\YourName\Downloads

# Set proper permissions on key (Windows)
icacls "ssh-key-2025-01-27.key" /inheritance:r
icacls "ssh-key-2025-01-27.key" /grant:r "%username%:R"

# Connect (replace with YOUR IP and YOUR key filename)
ssh -i ssh-key-2025-01-27.key ubuntu@YOUR_ORACLE_IP
```

**On Mac/Linux**:

```bash
# Set proper permissions
chmod 400 ~/Downloads/ssh-key-2025-01-27.key

# Connect
ssh -i ~/Downloads/ssh-key-2025-01-27.key ubuntu@YOUR_ORACLE_IP
```

**If asked "Are you sure you want to continue?"** → Type `yes` and press Enter

**You should see**:
```
Welcome to Ubuntu 22.04 LTS
...
ubuntu@sfsu-chatbot:~$
```

✅ **You're connected to your Oracle Cloud instance!**

---

## 📋 Part 4: Configure Ubuntu Firewall

Oracle has TWO firewalls - we configured cloud-level, now configure OS-level:

```bash
# Allow ports
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 443 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 8000 -j ACCEPT

# Save rules
sudo netfilter-persistent save

# Or if that doesn't work:
sudo apt install iptables-persistent -y
```

---

## 📋 Part 5: Install Dependencies

### Step 7: Update System

```bash
sudo apt update && sudo apt upgrade -y
```

This takes 5-10 minutes. Wait for it to complete.

---

### Step 8: Install Python 3.11

```bash
# Add Python repository
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3.11-dev python3-pip -y

# Verify
python3.11 --version
# Should show: Python 3.11.x
```

---

### Step 9: Install Node.js (for frontend build)

```bash
# Install Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install nodejs -y

# Verify
node --version
# Should show: v20.x.x

npm --version
# Should show: 10.x.x
```

---

### Step 10: Install Nginx

```bash
sudo apt install nginx -y

# Start Nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Check status
sudo systemctl status nginx
# Should show "active (running)"
```

**Test**: Visit `http://YOUR_ORACLE_IP` in browser
- Should see "Welcome to nginx!" page ✅

---

### Step 11: Install Ollama (ARM version)

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Verify Ollama is running
sudo systemctl status ollama
# Should show "active (running)"
```

---

### Step 12: Pull DeepSeek R1 Model

**This takes 5-10 minutes** - downloading ~4GB model:

```bash
# Pull model
ollama pull deepseek-r1:7b

# Wait for download to complete...
# You'll see progress bars

# Test model works
ollama run deepseek-r1:7b "Hello, test message"

# You should see a response!
# Press Ctrl+D to exit
```

✅ **Ollama + DeepSeek R1 is working on Oracle Cloud!**

---

## 📋 Part 6: Deploy Your Application

### Step 13: Upload Your Code

**Option A: If your code is on GitHub**:

```bash
cd /home/ubuntu
git clone https://github.com/YOUR_USERNAME/sfsu-cs-chatbot.git
cd sfsu-cs-chatbot
```

**Option B: If code NOT on GitHub, upload from local machine**:

**First, on your local machine**:
```bash
# Navigate to your project
cd D:\sfsu-cs-chatbot

# Create zip of backend
tar -czf backend.tar.gz backend

# Create zip of frontend
tar -czf frontend.tar.gz frontend

# Upload to Oracle (replace with your key and IP)
scp -i "C:\Users\YourName\Downloads\ssh-key-2025-01-27.key" backend.tar.gz ubuntu@YOUR_ORACLE_IP:/home/ubuntu/
scp -i "C:\Users\YourName\Downloads\ssh-key-2025-01-27.key" frontend.tar.gz ubuntu@YOUR_ORACLE_IP:/home/ubuntu/
```

**Then, on Oracle instance**:
```bash
cd /home/ubuntu

# Extract files
tar -xzf backend.tar.gz
tar -xzf frontend.tar.gz

# Create project structure
mkdir -p sfsu-cs-chatbot
mv backend sfsu-cs-chatbot/
mv frontend sfsu-cs-chatbot/
cd sfsu-cs-chatbot
```

---

### Step 14: Set Up Backend

```bash
cd /home/ubuntu/sfsu-cs-chatbot/backend

# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install requirements
pip install --upgrade pip
pip install -r requirements.txt
```

**This takes 5-10 minutes** - installing all Python packages.

---

### Step 15: Create Backend Environment File

```bash
nano .env
```

**Paste this** (replace with YOUR actual values):

```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_DB_PASSWORD=your_db_password

# Web Search
SERPAPI_KEY=your_serpapi_key

# JWT Secret (generate random string)
JWT_SECRET=your_random_32_character_secret_key_here

# Email Service
RESEND_API_KEY=your_resend_api_key
SENDER_EMAIL=noreply@yourdomain.com

# Environment
ENVIRONMENT=production

# Ollama (runs locally on same instance)
# No configuration needed - defaults to localhost:11434
```

**Save**: Press `Ctrl+X`, then `Y`, then `Enter`

---

### Step 16: Test Backend Locally

```bash
# Make sure you're in backend directory with venv activated
cd /home/ubuntu/sfsu-cs-chatbot/backend
source venv/bin/activate

# Run backend
python main.py

# Should see:
# INFO:     Started server process
# INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Open NEW SSH session** (keep first one running):

```bash
# Test health endpoint
curl http://localhost:8000/health

# Should return: {"status":"healthy"}
```

**If working** → Press `Ctrl+C` in first terminal to stop backend ✅

---

## 📋 Part 7: Configure Backend as System Service

### Step 17: Create Systemd Service

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

**Save**: `Ctrl+X`, `Y`, `Enter`

---

### Step 18: Start Backend Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable sfsu-chatbot

# Start service
sudo systemctl start sfsu-chatbot

# Check status
sudo systemctl status sfsu-chatbot
```

**You should see**: "active (running)" in green ✅

**Test**:
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy"}
```

---

## 📋 Part 8: Deploy Frontend

### Step 19: Build Frontend

```bash
cd /home/ubuntu/sfsu-cs-chatbot/frontend

# Create .env for production
nano .env
```

**Paste**:
```env
VITE_API_URL=/api
```

**Save**: `Ctrl+X`, `Y`, `Enter`

**Install and build**:
```bash
# Install dependencies (takes 2-3 minutes)
npm install

# Build for production (takes 1-2 minutes)
npm run build

# This creates 'dist' folder with production build
ls dist
# Should see: index.html, assets, etc.
```

---

## 📋 Part 9: Configure Nginx

### Step 20: Configure Nginx to Serve App

```bash
sudo nano /etc/nginx/sites-available/default
```

**Delete everything and paste this**:

```nginx
server {
    listen 80 default_server;
    listen [::]:80 default_server;

    server_name _;

    root /home/ubuntu/sfsu-cs-chatbot/frontend/dist;
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

---

### Step 21: Set Permissions and Restart Nginx

```bash
# Give Nginx permission to read frontend files
sudo chmod -R 755 /home/ubuntu/sfsu-cs-chatbot/frontend/dist

# Test Nginx configuration
sudo nginx -t
# Should say: "test is successful"

# Restart Nginx
sudo systemctl restart nginx

# Check status
sudo systemctl status nginx
# Should show: "active (running)"
```

---

## 📋 Part 10: Run Database Migrations

### Step 22: Run SQL in Supabase

**Don't forget** - you need to run these SQL migrations in Supabase!

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

### Step 23: Test Your Deployment

**Visit**: `http://YOUR_ORACLE_IP`

You should see your chatbot! 🎉

**Test everything**:
1. ✅ Ask a question: "What is CS 101?"
2. ✅ Verify response (should work!)
3. ✅ Check no [Local] or [Web] tags
4. ✅ Test flag incorrect feature
5. ✅ Test professor login
6. ✅ Test notifications
7. ✅ Test view corrections

---

## 🔗 Share Your Link!

**Your public URL**: `http://YOUR_ORACLE_IP`

Example: `http://123.45.67.89`

**Share this with**:
- Professors for review
- Classmates for testing
- Anyone with internet access!

---

## 🛠️ Management Commands

### View Backend Logs:
```bash
sudo journalctl -u sfsu-chatbot -f
```

### Restart Backend:
```bash
sudo systemctl restart sfsu-chatbot
```

### Check Backend Status:
```bash
sudo systemctl status sfsu-chatbot
```

### Restart Ollama:
```bash
sudo systemctl restart ollama
```

### Check Ollama:
```bash
ollama list
# Should show: deepseek-r1:7b

ollama ps
# Shows running models
```

### Restart Nginx:
```bash
sudo systemctl restart nginx
```

### Check All Services:
```bash
sudo systemctl status sfsu-chatbot
sudo systemctl status ollama
sudo systemctl status nginx
```

---

## 🔄 Update Your Application

### Update Backend Code:

**If using GitHub**:
```bash
cd /home/ubuntu/sfsu-cs-chatbot
git pull
sudo systemctl restart sfsu-chatbot
```

**If uploading manually**:
```bash
# On local machine, upload new backend files
scp -i key.pem -r D:\sfsu-cs-chatbot\backend ubuntu@YOUR_IP:/home/ubuntu/sfsu-cs-chatbot/

# On Oracle, restart
sudo systemctl restart sfsu-chatbot
```

### Update Frontend:

```bash
cd /home/ubuntu/sfsu-cs-chatbot/frontend
npm run build
sudo systemctl restart nginx
```

---

## 📊 Monitor Resources

### Check Memory Usage:
```bash
free -h
# Shows: 24GB total, how much used
```

### Check Disk Space:
```bash
df -h
# Shows: 100GB total, how much used
```

### Check CPU:
```bash
htop
# Interactive process viewer
# Press 'q' to quit
```

### Check Ollama Memory:
```bash
ollama ps
# Shows which models are loaded and memory usage
```

---

## 🐛 Troubleshooting

### Issue: Can't SSH into instance

**Check**:
1. Using correct key file
2. Using correct IP address
3. Security list allows port 22
4. Key has correct permissions

**Fix**:
```bash
# On Windows
icacls "key.pem" /inheritance:r
icacls "key.pem" /grant:r "%username%:R"

# On Mac/Linux
chmod 400 key.pem
```

---

### Issue: Can't access website (Connection refused)

**Check**:
1. Backend is running: `sudo systemctl status sfsu-chatbot`
2. Nginx is running: `sudo systemctl status nginx`
3. Firewall rules added in Oracle Cloud Console
4. Ubuntu firewall configured: `sudo iptables -L`

**Fix**:
```bash
# Restart everything
sudo systemctl restart sfsu-chatbot
sudo systemctl restart nginx

# Re-add firewall rules
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT
sudo netfilter-persistent save
```

---

### Issue: Frontend loads but "Network Error"

**Check**:
1. Backend is running: `curl http://localhost:8000/health`
2. Check backend logs: `sudo journalctl -u sfsu-chatbot -f`
3. CORS settings in backend allow your IP

**Fix**:
```bash
# Check backend logs for errors
sudo journalctl -u sfsu-chatbot -n 50

# Restart backend
sudo systemctl restart sfsu-chatbot
```

---

### Issue: Ollama not responding / Slow

**Check**:
```bash
# Check if Ollama is running
sudo systemctl status ollama

# Check memory
free -h

# Check if model is loaded
ollama ps
```

**Fix**:
```bash
# Restart Ollama
sudo systemctl restart ollama

# Reload model
ollama run deepseek-r1:7b "test"
# Press Ctrl+D
```

---

### Issue: Out of disk space

**Check**:
```bash
df -h
# If /dev/sda1 is >90% full
```

**Fix**:
```bash
# Clean old logs
sudo journalctl --vacuum-time=7d

# Clean apt cache
sudo apt clean

# Remove old kernels
sudo apt autoremove -y
```

---

## 🔒 Security Best Practices

### 1. Update SSH to Key-Only (Disable Password)

```bash
sudo nano /etc/ssh/sshd_config

# Find and change these lines:
PasswordAuthentication no
PubkeyAuthentication yes

# Save and restart SSH
sudo systemctl restart sshd
```

### 2. Set Up Automatic Security Updates

```bash
sudo apt install unattended-upgrades -y
sudo dpkg-reconfigure -plow unattended-upgrades
# Select "Yes"
```

### 3. Create Non-Root User (Optional)

```bash
# Add new user
sudo adduser chatbotuser

# Add to sudo group
sudo usermod -aG sudo chatbotuser

# Test
su - chatbotuser
```

### 4. Set Up Firewall Monitoring

```bash
# Install fail2ban (blocks brute force)
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

## 💰 Cost Monitoring

### Check You're Using Always Free Resources:

1. Go to Oracle Cloud Console
2. Click hamburger menu → **Billing & Cost Management** → **Cost Analysis**
3. Should show: **$0.00**

**Always Free Resources Include**:
- ✅ 4 ARM vCPU + 24GB RAM (what you're using)
- ✅ 200GB Block Volume (you're using 100GB)
- ✅ 10TB bandwidth/month
- ✅ Free forever (not a trial!)

**Make sure**:
- You selected "VM.Standard.A1.Flex" shape
- You didn't add extra paid services

---

## ✅ Final Checklist

- [ ] Oracle Cloud account created
- [ ] Compute instance created (4 vCPU, 24GB RAM)
- [ ] Security rules added (ports 22, 80, 443, 8000)
- [ ] Ubuntu firewall configured
- [ ] Python 3.11 installed
- [ ] Node.js installed
- [ ] Nginx installed
- [ ] Ollama installed
- [ ] DeepSeek R1 model pulled
- [ ] Backend code deployed
- [ ] Backend .env configured
- [ ] Backend running as service
- [ ] Frontend built
- [ ] Nginx configured
- [ ] SQL migrations run in Supabase
- [ ] Can access website at http://YOUR_IP
- [ ] Chat works
- [ ] All features tested (flag, notifications, etc.)
- [ ] Shared link with professor

---

## 🎉 Congratulations!

You now have:
- ✅ **24/7 uptime** chatbot
- ✅ **Ollama + DeepSeek R1** running in cloud
- ✅ **$0 cost** (FREE forever!)
- ✅ **Public URL** to share
- ✅ **Professional deployment**
- ✅ **NO rate limits**
- ✅ **Full control**

**Your URL**: `http://YOUR_ORACLE_IP`

**Share it with**:
- Professors for review ✅
- Students for testing ✅
- Anyone with internet! ✅

---

## 📞 Need Help?

**Oracle Cloud Resources**:
- Documentation: https://docs.oracle.com/en-us/iaas/Content/home.htm
- Community Forums: https://cloudcustomerconnect.oracle.com/

**Check logs first**:
```bash
sudo journalctl -u sfsu-chatbot -f    # Backend logs
sudo journalctl -u ollama -f          # Ollama logs
sudo tail -f /var/log/nginx/error.log # Nginx errors
```

---

**TIME**: 2-3 hours total
**COST**: $0 (FREE forever)
**RESULT**: Professional 24/7 chatbot with Ollama! 🚀

**You're LIVE on Oracle Cloud!** 🎉
