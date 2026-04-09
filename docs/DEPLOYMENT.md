# Deployment Guide — AWS Lightsail

Deploy SageDocs to a 2GB AWS Lightsail VM using Apache as reverse proxy, uvicorn as the ASGI server, and systemd for process management.

## Architecture

```
Internet → Apache (SSL + reverse proxy) → uvicorn :8100 → FastAPI app
                                           ↑ managed by systemd
```

## Prerequisites

- AWS account with Lightsail access
- Domain name pointed to the server (e.g., `aichatbot.ignitx.solutions`)
- OpenAI and/or Anthropic API key(s)

---

## Step 1: Create Lightsail Instance

1. Go to AWS Lightsail console
2. Create a new instance with:
   - **OS:** Ubuntu 22.04 LTS
   - **Plan:** 2 GB RAM / 1 vCPU / 60 GB SSD ($12/mo)
3. Assign a **static IP** to the instance
4. In the **Networking** tab, open ports: **22** (SSH), **80** (HTTP), **443** (HTTPS)

## Step 2: Point DNS

Add an **A record** for your domain pointing to the Lightsail static IP:

```
aichatbot.ignitx.solutions → <static-ip>
```

Allow a few minutes for DNS propagation.

## Step 3: Server Setup

SSH into the instance and install system dependencies:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-dev \
    build-essential apache2 certbot python3-certbot-apache git
```

## Step 4: Deploy App Code

The repo is cloned at `/home/ubuntu/SageDocs`. Use the deploy script to sync it to the deployment directory:

```bash
# First-time deploy: creates venv, data dirs, syncs code, installs deps
sudo bash /home/ubuntu/SageDocs/scripts/deploy.sh
```

The script uses `rsync` to copy code from `/home/ubuntu/SageDocs` to `/var/www/sagedocs`, preserving `.env`, `venv/`, `data/`, and `uploads/` in the deploy directory.

For subsequent deploys after code changes:

```bash
# Code-only update: syncs code, updates deps, restarts service (skips venv/dir setup)
sudo bash /home/ubuntu/SageDocs/scripts/deploy.sh --update
```

<details>
<summary>Manual setup (alternative)</summary>

```bash
sudo mkdir -p /var/www/sagedocs
sudo chown $USER:$USER /var/www/sagedocs
cd /var/www/sagedocs
git clone <your-repo-url> .
python3 -m venv venv
source venv/bin/activate
cd backend
pip install -r requirements.txt
```
</details>

## Step 5: Configure Environment

Create `/var/www/sagedocs/backend/.env`:

```ini
# LLM Provider (openai or anthropic)
LLM_PROVIDER=openai
OPENAI_API_KEY=<your-openai-key>
ANTHROPIC_API_KEY=<your-anthropic-key>

# Models
LLM_MODEL=gpt-5.2
LLM_MODEL_FAST=gpt-5-mini
EMBEDDING_MODEL=text-embedding-3-large

# ChromaDB
CHROMA_PERSIST_DIR=./data/chroma

# Logging — DEBUG for verbose RAG pipeline tracing, INFO for production
LOG_LEVEL=INFO

# Server — bind to localhost only; Apache handles external traffic
HOST=127.0.0.1
PORT=8100

# CORS — comma-separated allowed origins
CORS_ORIGINS=https://aichatbot.ignitx.solutions,https://your-host-app.com

# Admin
ADMIN_SECRET_KEY=<generate-a-random-secret>
ADMIN_USERNAME=admin
ADMIN_PASSWORD=<strong-admin-password>
JWT_SECRET=<generate-a-random-jwt-secret>
```

> **Important:** Set `HOST=127.0.0.1` (not `0.0.0.0`) so uvicorn only accepts local connections. Apache handles all external traffic.

## Step 6: Set Up Data Directories

```bash
cd /var/www/sagedocs/backend
mkdir -p data/chroma data/images data/analytics data/tenants uploads
chmod -R 755 data uploads
```

## Step 7: Create systemd Service

Create `/etc/systemd/system/sagedocs.service`:

```ini
[Unit]
Description=SageDocs
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/sagedocs/backend
ExecStart=/var/www/sagedocs/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8100
Restart=always
RestartSec=5
EnvironmentFile=/var/www/sagedocs/backend/.env

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
# Set ownership
sudo chown -R www-data:www-data /var/www/sagedocs

# Start the service
sudo systemctl daemon-reload
sudo systemctl enable sagedocs
sudo systemctl start sagedocs

# Verify
sudo systemctl status sagedocs
curl http://127.0.0.1:8100/health
```

## Step 8: Configure Apache as Reverse Proxy

Enable required Apache modules:

```bash
sudo a2enmod proxy proxy_http proxy_wstunnel headers ssl rewrite
```

Create `/etc/apache2/sites-available/sagedocs.conf`:

```apache
<VirtualHost *:80>
    ServerName aichatbot.ignitx.solutions

    # Redirect HTTP to HTTPS
    RewriteEngine On
    RewriteCond %{HTTPS} off
    RewriteRule ^ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]
</VirtualHost>

<VirtualHost *:443>
    ServerName aichatbot.ignitx.solutions

    # SSL — certbot will fill in certificate paths (Step 9)

    # Reverse proxy to uvicorn
    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:8100/
    ProxyPassReverse / http://127.0.0.1:8100/

    # SSE streaming support
    SetEnv proxy-sendchunked 1
    SetEnv proxy-sendcl 0

    # Forward client info
    RequestHeader set X-Forwarded-Proto "https"
    RequestHeader set X-Forwarded-For "%{REMOTE_ADDR}s"

    # Timeouts for long-running LLM requests
    ProxyTimeout 120
    Timeout 120

    ErrorLog ${APACHE_LOG_DIR}/sagedocs_error.log
    CustomLog ${APACHE_LOG_DIR}/sagedocs_access.log combined
</VirtualHost>
```

Activate the site:

```bash
sudo a2ensite sagedocs.conf
sudo a2dissite 000-default.conf
sudo systemctl restart apache2
```

## Step 9: SSL with Let's Encrypt

```bash
sudo certbot --apache -d aichatbot.ignitx.solutions
```

Follow the prompts. Certbot automatically configures the SSL VirtualHost and sets up auto-renewal.

Verify auto-renewal works:

```bash
sudo certbot renew --dry-run
```

## Step 10: Verify Deployment

```bash
curl https://aichatbot.ignitx.solutions/
curl https://aichatbot.ignitx.solutions/health
```

Then check in a browser:
- `https://aichatbot.ignitx.solutions/admin/` — admin dashboard
- Test the chat widget from a host app page

---

## Post-Deployment

### Useful Commands

```bash
# View live app logs
sudo journalctl -u sagedocs -f

# View only RAG pipeline logs (retrieval, filtering, reranking)
sudo journalctl -u sagedocs -f | grep rag_engine

# View only chat routing logs (help/data mode decisions)
sudo journalctl -u sagedocs -f | grep chat

# Enable verbose logging for debugging (edit .env then restart)
# Set LOG_LEVEL=DEBUG for full RAG pipeline detail (prompt sizes, all query params)
# Set LOG_LEVEL=INFO for standard production logging (recommended)

# Restart after code update
cd /var/www/sagedocs && git pull
sudo systemctl restart sagedocs

# Check Apache error logs
sudo tail -f /var/log/apache2/sagedocs_error.log

# Check service status
sudo systemctl status sagedocs
```

### Updating the App

```bash
# Pull latest in the git clone, sync to deploy dir, restart service
sudo bash /home/ubuntu/SageDocs/scripts/deploy.sh --update
```

### CI/CD with a Self-Hosted GitHub Actions Runner

The repo ships with `.github/workflows/deploy.yml`, which runs `scripts/deploy.sh --update` on a self-hosted runner whenever code is pushed to `main`. One-time setup on the server:

**1. Install the runner**

In GitHub: *Settings → Actions → Runners → New self-hosted runner* and follow the Linux x64 instructions. Install it as the `ubuntu` user under `/home/ubuntu/actions-runner`. When prompted for labels, add `sagedocs` (the workflow targets `[self-hosted, sagedocs]`).

**2. Install as a service**

```bash
cd /home/ubuntu/actions-runner
sudo ./svc.sh install ubuntu
sudo ./svc.sh start
```

**3. Grant passwordless sudo for the deploy script only**

The workflow runs `sudo -E bash scripts/deploy.sh --update`, so the runner user needs to invoke that one script without a password. Create `/etc/sudoers.d/sagedocs-runner`:

```
ubuntu ALL=(root) NOPASSWD: SETENV: /bin/bash /home/ubuntu/actions-runner/_work/sagedocs/sagedocs/scripts/deploy.sh *
```

Then `sudo visudo -c` to validate.

**4. Trigger a deploy**

Push to `main`, or run *Actions → Deploy to production → Run workflow* in GitHub. The runner will checkout into its work directory, run the deploy script with `SRC_DIR` pointed at the checkout, and the script will rsync to `/var/www/sagedocs` and restart the systemd unit.

**Notes**

- `/home/ubuntu/SageDocs` (the manual-deploy clone) is no longer needed once CI is wired up, but it's harmless to leave in place.
- The runner itself survives reboots via systemd (`actions.runner.*.service`).
- To check runner status: `sudo systemctl status 'actions.runner.*'`.

### Files Created on Server

| File | Purpose |
|---|---|
| `/var/www/sagedocs/backend/.env` | Environment configuration |
| `/etc/systemd/system/sagedocs.service` | systemd service unit |
| `/etc/apache2/sites-available/sagedocs.conf` | Apache virtual host |

### Troubleshooting

| Issue | Fix |
|---|---|
| `502 Bad Gateway` | Check if uvicorn is running: `sudo systemctl status sagedocs` |
| `503 Service Unavailable` | Check Apache modules: `sudo a2enmod proxy proxy_http` |
| App won't start | Check logs: `sudo journalctl -u sagedocs -e` |
| Permission errors | Fix ownership: `sudo chown -R www-data:www-data /var/www/sagedocs` |
| SSL certificate expired | Run: `sudo certbot renew` |
| Chat responses timeout | Increase `ProxyTimeout` in Apache config |
| Chat returns no answer | Set `LOG_LEVEL=DEBUG` in `.env`, restart, and check logs for similarity scores and threshold filtering. If all candidates are filtered, lower `SIMILARITY_THRESHOLD` |
| Documents uploaded but not found | Check logs for `"Very little text extracted"` warnings during ingestion — the document may not have parseable content |
