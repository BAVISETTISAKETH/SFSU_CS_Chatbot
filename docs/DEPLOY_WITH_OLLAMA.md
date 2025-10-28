# 🚀 Deploy to Production with Ollama

**Yes, you CAN use Ollama in production!**

**Advantages**:
- ✅ NO rate limits (unlike Groq's 14,400/day)
- ✅ FREE inference (no API costs)
- ✅ More privacy (data stays on your server)
- ✅ Use DeepSeek R1 (what you've been testing with)
- ✅ Full control

**Trade-offs**:
- ⚠️ Need a server to run Ollama
- ⚠️ Server costs ($10-40/month depending on specs)
- ⚠️ Need to manage server yourself

---

## 🎯 Three Options for Ollama in Production

### Option 1: All-in-One VPS (RECOMMENDED for Ollama)
**Deploy everything on one server**
- Frontend + Backend + Ollama on same VPS
- Simplest Ollama setup
- Cost: $15-40/month
- Time: 1-2 hours

### Option 2: Hybrid (Ollama Separate)
**Use cloud for frontend/backend, VPS for Ollama**
- Frontend: Vercel (free)
- Backend: Railway (free tier)
- Ollama: Separate VPS ($10/month)
- More complex networking
- Cost: $10-15/month

### Option 3: Cloud Ollama Services
**Use managed Ollama service**
- Services like Modal, RunPod, or Replicate
- They host Ollama for you
- Cost: Pay per use (~$0.0001-0.001 per request)
- Easiest but not free

---

## 🚀 OPTION 1: All-in-One VPS (RECOMMENDED)

### Overview:
- **Server**: DigitalOcean, Hetzner, or AWS
- **Specs**: 2 CPU, 4GB RAM minimum (8GB better for DeepSeek R1)
- **OS**: Ubuntu 22.04 LTS
- **Cost**: $15-40/month
- **Setup Time**: 1-2 hours

---

## Step 1: Choose Server Provider

### Recommended: Hetzner (Best Price/Performance)
- **CPX31**: 4 vCPU, 8GB RAM, 160GB SSD = **€10.20/month (~$12)**
- **Best for**: DeepSeek R1 7B
- Sign up: https://www.hetzner.com/cloud

### Alternative: DigitalOcean
- **Basic Droplet**: 2 vCPU, 4GB RAM, 80GB SSD = **$24/month**
- **Better Droplet**: 2 vCPU, 8GB RAM, 160GB SSD = **$48/month**
- Sign up: https://www.digitalocean.com/

### Alternative: AWS EC2
- **t3.large**: 2 vCPU, 8GB RAM = **~$60/month** (more expensive)
- More complex but more features

**For this guide, I'll use Hetzner (cheapest + good performance)**

---

## Step 2: Create Server

### On Hetzner:
1. Create account at https://www.hetzner.com/cloud
2. Create new project: "SFSU-Chatbot"
3. Click "Add Server"
4. Choose:
   - **Location**: Closest to you (e.g., Ashburn, VA for US West Coast)
   - **Image**: Ubuntu 22.04
   - **Type**: CPX31 (4 vCPU, 8GB RAM)
   - **Networking**: Public IPv4
   - **SSH Key**: Add your SSH key (or use password)
5. Click "Create & Buy"

**You'll get an IP address**: e.g., `123.45.67.89`

---

## Step 3: Connect to Server

```bash
ssh root@your_server_ip
```

---

## Step 4: Install Everything

### Update System
```bash
apt update && apt upgrade -y
```

### Install Python 3.11
```bash
apt install software-properties-common -y
add-apt-repository ppa:deadsnakes/ppa -y
apt update
apt install python3.11 python3.11-venv python3.11-dev python3-pip -y
```

### Install Node.js 20
```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install nodejs -y
```

### Install Nginx
```bash
apt install nginx -y
```

### Install Ollama
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Pull DeepSeek R1 Model
```bash
# This takes 5-10 minutes (downloading ~4GB)
ollama pull deepseek-r1:7b

# Verify it works
ollama run deepseek-r1:7b "Hello, test message"
# (Press Ctrl+D to exit)
```

---

## Step 5: Deploy Application

### Clone Repository
```bash
cd /var/www
git clone https://github.com/YOUR_USERNAME/sfsu-cs-chatbot.git
cd sfsu-cs-chatbot
```

If you don't have it on GitHub yet:
```bash
# On your local machine first:
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/sfsu-cs-chatbot.git
git push -u origin main

# Then on server, run the clone command above
```

---

### Set Up Backend
```bash
cd /var/www/sfsu-cs-chatbot/backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Create Backend .env
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

# Ollama (running locally on same server)
# No need to set - defaults to http://localhost:11434
```

**Save**: Ctrl+X, Y, Enter

---

### Build Frontend
```bash
cd /var/www/sfsu-cs-chatbot/frontend

# Create .env for production
nano .env
```

**Paste**:
```env
# Backend will be at /api endpoint (proxied by Nginx)
VITE_API_URL=/api
```

**Save**: Ctrl+X, Y, Enter

**Build**:
```bash
npm install
npm run build
```

This creates `/var/www/sfsu-cs-chatbot/frontend/dist` with production build.

---

## Step 6: Configure Systemd Service

### Create Backend Service
```bash
nano /etc/systemd/system/sfsu-chatbot-backend.service
```

**Paste**:
```ini
[Unit]
Description=SFSU Chatbot Backend API
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/var/www/sfsu-cs-chatbot/backend
Environment="PATH=/var/www/sfsu-cs-chatbot/backend/venv/bin"
ExecStart=/var/www/sfsu-cs-chatbot/backend/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Save**: Ctrl+X, Y, Enter

### Enable and Start Backend
```bash
systemctl daemon-reload
systemctl enable sfsu-chatbot-backend
systemctl start sfsu-chatbot-backend

# Check status
systemctl status sfsu-chatbot-backend
```

**Expected**: Should see "active (running)" ✅

---

## Step 7: Configure Nginx

```bash
nano /etc/nginx/sites-available/sfsu-chatbot
```

**Paste**:
```nginx
server {
    listen 80;
    server_name your_domain.com;  # Or use your server IP

    # Frontend (React app)
    location / {
        root /var/www/sfsu-cs-chatbot/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
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
}
```

**Save**: Ctrl+X, Y, Enter

### Enable Site
```bash
# Remove default site
rm /etc/nginx/sites-enabled/default

# Enable our site
ln -s /etc/nginx/sites-available/sfsu-chatbot /etc/nginx/sites-enabled/

# Test configuration
nginx -t

# Restart Nginx
systemctl restart nginx
```

---

## Step 8: Configure Firewall

```bash
# Allow HTTP, HTTPS, and SSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 22/tcp

# Enable firewall
ufw --force enable

# Check status
ufw status
```

---

## Step 9: Set Up SSL (HTTPS) - Optional but Recommended

### Get Free SSL with Let's Encrypt

First, you need a domain name. If you have one:

```bash
# Install Certbot
apt install certbot python3-certbot-nginx -y

# Get certificate (replace with your domain)
certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Follow prompts - it will ask for email and agree to terms
```

**If you don't have a domain**: You can still access via `http://your_server_ip`

---

## Step 10: Run SQL Migrations in Supabase

Don't forget to run these in Supabase SQL Editor:

```sql
-- 1. Add session_id to corrections
ALTER TABLE corrections
ADD COLUMN IF NOT EXISTS session_id VARCHAR(100);

CREATE INDEX IF NOT EXISTS corrections_session_id_idx ON corrections(session_id);

-- 2. Create notifications table
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

---

## Step 11: Test Your Production App

### Access Your App
- **With domain**: `https://yourdomain.com`
- **Without domain**: `http://your_server_ip`

### Test Everything:
1. ✅ Chat works
2. ✅ Responses don't have [Local] tags
3. ✅ Flag incorrect works
4. ✅ Professor dashboard accessible
5. ✅ Notifications work
6. ✅ View corrections works

---

## Step 12: Monitor and Maintain

### View Backend Logs
```bash
journalctl -u sfsu-chatbot-backend -f
```

### View Nginx Logs
```bash
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Restart Services if Needed
```bash
systemctl restart sfsu-chatbot-backend
systemctl restart nginx
```

### Update Application
```bash
cd /var/www/sfsu-cs-chatbot

# Pull latest code
git pull

# Update backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
systemctl restart sfsu-chatbot-backend

# Update frontend
cd ../frontend
npm install
npm run build

# No need to restart - Nginx serves static files
```

---

## 🔧 Troubleshooting

### Issue: Ollama not responding
```bash
# Check if Ollama is running
systemctl status ollama

# Restart Ollama
systemctl restart ollama

# Test Ollama
ollama list
ollama run deepseek-r1:7b "test"
```

### Issue: Backend won't start
```bash
# Check logs
journalctl -u sfsu-chatbot-backend -n 50

# Common issues:
# - Missing environment variables in backend/.env
# - Port 8000 already in use
# - Python dependencies not installed
```

### Issue: "Network Error" in frontend
```bash
# Check backend is running
systemctl status sfsu-chatbot-backend

# Check Nginx configuration
nginx -t

# Check backend logs
journalctl -u sfsu-chatbot-backend -f
```

### Issue: Slow responses
```bash
# Check server resources
htop

# If RAM is full, upgrade server or reduce Ollama model size
# Alternatively, restart Ollama:
systemctl restart ollama
```

---

## 💰 Cost Comparison

### With Ollama (VPS):
- **Hetzner CPX31**: €10.20/month (~$12)
- **Domain** (optional): $10-15/year
- **Supabase**: Free tier
- **SerpAPI**: Free 100/month
- **Resend**: Free 100/day
- **Total**: **$12-15/month**

### With Groq (Cloud):
- **Vercel**: Free
- **Railway**: Free $5 credit/month
- **Groq**: Free (14,400 req/day)
- **Supabase**: Free tier
- **Total**: **$0-5/month**
- **Limitation**: Rate limits

---

## 📊 When to Use Ollama vs Groq

### Use Ollama (VPS) If:
- ✅ You expect high traffic (>14,400 requests/day)
- ✅ You want NO rate limits
- ✅ You care about data privacy
- ✅ You're comfortable managing a server
- ✅ Budget: $12-15/month is acceptable

### Use Groq (Cloud) If:
- ✅ You want simplest deployment
- ✅ Low-medium traffic is expected
- ✅ Budget: Free is better
- ✅ You don't want to manage servers
- ✅ 14,400 requests/day is enough

---

## 🎉 Success!

Your chatbot is now running in production with Ollama! 🚀

**What you have**:
- ✅ Full control over LLM
- ✅ NO rate limits
- ✅ DeepSeek R1 (what you tested with)
- ✅ All features working
- ✅ HTTPS (if you set up domain)
- ✅ Auto-restart on crashes
- ✅ Production-ready

**Next steps**:
1. Create professor accounts (`add_admin.py` on server)
2. Share URL with students
3. Monitor server performance
4. Set up automatic backups

---

## 🔄 Quick Commands Reference

```bash
# SSH to server
ssh root@your_server_ip

# Check backend status
systemctl status sfsu-chatbot-backend

# View backend logs
journalctl -u sfsu-chatbot-backend -f

# Restart backend
systemctl restart sfsu-chatbot-backend

# Check Ollama status
systemctl status ollama
ollama list

# Restart Ollama
systemctl restart ollama

# Update app
cd /var/www/sfsu-cs-chatbot && git pull
systemctl restart sfsu-chatbot-backend
cd frontend && npm run build

# Monitor server resources
htop
df -h  # Disk space
free -m  # Memory
```

---

**Time to Deploy**: 1-2 hours
**Monthly Cost**: $12-15
**Rate Limits**: NONE
**Control**: FULL

**Deploy with confidence!** 🚀
