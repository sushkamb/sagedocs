# Build and Test Guide

Step-by-step instructions for setting up, running, testing, and deploying ForteAI Bot.

---

## 1. Prerequisites

- **Python 3.11+** — [Download](https://www.python.org/downloads/)
- **pip** — Comes with Python
- **Git** — For version control
- **Docker** (optional) — For containerized deployment
- **An LLM API key** — OpenAI (recommended) or Anthropic

Verify your Python version:

```bash
python3 --version
# Should output: Python 3.11.x or higher
```

---

## 2. Local Development Setup

### 2.1 Clone and Install

```bash
git clone <repo-url>
cd forteaibot/backend

# Create a virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2.2 Configure Environment

```bash
# Copy the example config
cp ../.env.example .env
```

Edit `.env` and set at minimum:

```
OPENAI_API_KEY=sk-your-actual-key-here
```

All other settings have sensible defaults for local development.

### 2.3 Run the Server

```bash
# From the backend/ directory, with venv activated
uvicorn app.main:app --reload --port 8500
```

You should see:

```
INFO:     Uvicorn running on http://0.0.0.0:8500 (Press CTRL+C to quit)
INFO:     Started reloader process
```

### 2.4 Verify

- Open http://localhost:8500 — Should return `{"name":"ForteAI Bot","version":"0.1.0","status":"running","docs":"/docs"}`
- Open http://localhost:8500/docs — Swagger UI with all API endpoints
- Open http://localhost:8500/admin — Admin dashboard

---

## 3. Testing the Help Mode (RAG)

### 3.1 Create a Tenant

Use the admin JWT token obtained from `/api/admin/login` (see section 3.2 for login steps):

```bash
curl -X POST http://localhost:8500/api/tenants/create \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "tenant_id": "chirocloud",
    "display_name": "ChiroCloud",
    "welcome_message": "Hi! Ask me anything about ChiroCloud.",
    "starter_questions": [
      "How do I add a new patient?",
      "How do I submit a claim?",
      "How do I schedule an appointment?"
    ]
  }'
```

### 3.2 Upload a Test Document

Create a simple test markdown file:

```bash
cat > /tmp/test-help.md << 'EOF'
# Getting Started with ChiroCloud

## Adding a New Patient

1. Click "Patients" in the left sidebar
2. Click the "New Patient" button at the top right
3. Fill in the required fields: First Name, Last Name, Date of Birth
4. Click "Save" to create the patient record

## Scheduling an Appointment

1. Go to the "Schedule" tab
2. Click on an empty time slot
3. Search for the patient by name
4. Select the appointment type
5. Click "Save" to confirm the appointment

## Submitting a Claim

1. Open the patient's visit record
2. Ensure all diagnosis codes and procedure codes are entered
3. Click "Billing" tab
4. Click "Submit Claim"
5. Select the insurance payer
6. Click "Send" to submit electronically
EOF
```

First, obtain an admin JWT token:

```bash
curl -X POST http://localhost:8500/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "change-this-password"}'
# → { "token": "eyJ...", "expires_in": 86400 }
```

Upload it (replace `YOUR_TOKEN` with the token from the login response):

```bash
curl -X POST http://localhost:8500/api/documents/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/tmp/test-help.md" \
  -F "tenant=chirocloud" \
  -F "title=Getting Started Guide"
```

Expected response:

```json
{
  "message": "Document 'Getting Started Guide' indexed successfully",
  "filename": "test-help.md",
  "chunk_count": 3
}
```

### 3.3 Test a Chat Query

```bash
curl -X POST http://localhost:8500/api/chat/help \
  -H "Content-Type: application/json" \
  -d '{
    "tenant": "chirocloud",
    "message": "How do I add a new patient?"
  }'
```

Expected: A response with the answer pulled from the uploaded document, with source references.

### 3.4 Verify via Admin Dashboard

1. Open http://localhost:8500/admin
2. Select "chirocloud" from the tenant dropdown
3. You should see the uploaded document listed under "Indexed Documents"
4. Switch to the "Test Chat" tab and ask a question interactively

---

## 4. Testing the External Document Upload API

The external API allows external services to upload documents using per-tenant API keys.

### 4.1 Generate an API Key

Use the admin JWT token obtained from `/api/admin/login`:

```bash
curl -X POST http://localhost:8500/api/tenants/chirocloud/api-key \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Response (save the `api_key` — it cannot be retrieved again):

```json
{
  "tenant_id": "chirocloud",
  "api_key": "fai_abc123...",
  "message": "Save this key now — it cannot be retrieved again."
}
```

### 4.2 Upload a Document with the API Key

```bash
curl -X POST http://localhost:8500/api/v1/documents/upload \
  -H "X-API-Key: fai_abc123..." \
  -F "file=@/tmp/test-help.md" \
  -F "title=External Upload Test"
```

Expected response:

```json
{
  "success": true,
  "message": "Document 'External Upload Test' indexed successfully",
  "filename": "test-help.md",
  "chunk_count": 3
}
```

### 4.3 Verify Authentication

Bad or missing API key should return 401:

```bash
curl -X POST http://localhost:8500/api/v1/documents/upload \
  -H "X-API-Key: bad_key" \
  -F "file=@/tmp/test-help.md" \
  -F "title=Should Fail"
# → {"detail": "Invalid API key"}
```

---

## 5. Testing the Widget

### 4.1 Create a Test HTML Page

Create a file anywhere on your machine:

```html
<!DOCTYPE html>
<html>
<head><title>Widget Test</title></head>
<body>
  <h1>ForteAI Widget Test Page</h1>
  <p>The chat widget should appear in the bottom-right corner.</p>

  <script src="http://localhost:8500/widget/forteai-widget.js"></script>
  <script>
    ForteAI.init({
      tenant: 'chirocloud',
      apiUrl: 'http://localhost:8500'
    });
  </script>
</body>
</html>
```

Open this file in a browser. You should see a blue chat bubble in the bottom-right corner. Click it and ask a question.

---

## 6. Testing the Data Mode (Function Calling)

Data mode requires a running host application with API endpoints. For local testing without the host app, you can verify the tool registry loads correctly:

### 6.1 Verify Tool Registry

```bash
curl http://localhost:8500/docs
```

Navigate to the `POST /api/chat/data` endpoint in Swagger. The tool registry is loaded from `backend/tools/chirocloud.yaml`.

### 6.2 Mock Testing

To test data mode end-to-end without ChiroCloud running, you can temporarily modify `chirocloud.yaml` to point `base_url` to a mock API:

```bash
# Start a simple mock server (in a separate terminal)
python3 -c "
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'count': 42}).encode())

HTTPServer(('', 9999), Handler).serve_forever()
"
```

Update `backend/tools/chirocloud.yaml`:

```yaml
base_url: http://localhost:9999
```

Then test:

```bash
curl -X POST http://localhost:8500/api/chat/data \
  -H "Content-Type: application/json" \
  -d '{
    "tenant": "chirocloud",
    "account_number": "TEST001",
    "token": "test-token",
    "message": "How many new patients this month?"
  }'
```

---

## 7. API Testing with Swagger

FastAPI auto-generates interactive API documentation:

- **Swagger UI:** http://localhost:8500/docs
- **ReDoc:** http://localhost:8500/redoc

You can test all endpoints directly from the Swagger UI without needing curl.

---

## 8. Running with Docker

### 8.1 Build the Image

```bash
cd backend
docker build -t forteai .
```

### 8.2 Run the Container

```bash
docker run -d \
  --name forteai \
  -p 8500:8500 \
  --env-file ../.env \
  -v forteai-data:/app/data \
  forteai
```

The `-v forteai-data:/app/data` flag persists ChromaDB data and tenant configs across container restarts.

### 8.3 Verify

```bash
curl http://localhost:8500/health
# {"status":"healthy"}
```

### 8.4 View Logs

```bash
docker logs -f forteai
```

---

## 9. Deploying to AWS EC2

### 9.1 Prepare the Server

```bash
# Install Docker on Amazon Linux 2
sudo yum update -y
sudo yum install -y docker
sudo service docker start
sudo usermod -aG docker ec2-user
```

### 9.2 Deploy

```bash
# Transfer the code to the server (or pull from git)
git clone <repo-url>
cd forteaibot

# Create .env with production settings
cp .env.example .env
# Edit .env: set CORS_ORIGINS to your app's domain, set API keys

# Build and run
cd backend
docker build -t forteai .
docker run -d \
  --name forteai \
  -p 8500:8500 \
  --restart unless-stopped \
  --env-file ../.env \
  -v forteai-data:/app/data \
  forteai
```

### 9.3 Security Checklist

- [ ] Set `CORS_ORIGINS` to only your app's domain(s)
- [ ] Set a strong `ADMIN_SECRET_KEY` (protects external API key generation)
- [ ] Set a strong `ADMIN_PASSWORD` and `JWT_SECRET` (protects admin dashboard)
- [ ] Use HTTPS (put behind an ALB or nginx with SSL)
- [ ] Keep API keys in `.env` only (never commit to git)
- [ ] Store tenant API keys securely — they are shown only once at generation time
- [ ] Restrict EC2 security group: port 8500 accessible only from your app servers or load balancer
- [ ] Set up CloudWatch or similar for monitoring

---

## 10. Troubleshooting

### Server won't start

- Verify Python 3.11+: `python3 --version`
- Verify venv is activated: `which python` should point to your venv
- Check `.env` exists and has valid API key

### "Module not found" errors

```bash
pip install -r requirements.txt
```

### ChromaDB permission errors

```bash
# Ensure the data directory exists and is writable
mkdir -p data/chroma
chmod 755 data/chroma
```

### Widget not appearing

- Check browser console for CORS errors
- Ensure `CORS_ORIGINS` in `.env` includes the page's origin
- Verify the ForteAI server is running and accessible from the browser

### Chat returns "I don't have any documentation"

- Verify documents are uploaded: `curl http://localhost:8500/api/documents/list?tenant=chirocloud`
- Re-upload documents if the list is empty
- Check that the tenant name in the widget matches the tenant used during upload

### Docker container exits immediately

```bash
docker logs forteai
```

Common cause: missing `.env` file or invalid API key.

---

## 11. Development Workflow

### Adding Help Content

1. Open the admin dashboard at `/admin`
2. Select the tenant
3. Upload PDF, HTML, or Markdown files with descriptive titles
4. Test using the "Test Chat" tab
5. Check "Analytics" for unanswered questions to identify content gaps

### Adding a New Data Query Tool

1. Define the tool in `backend/tools/{tenant}.yaml`:

```yaml
  - name: get_new_metric
    description: "Description the LLM uses to decide when to call this tool"
    endpoint: /api/assistant/your-endpoint
    method: GET
    parameters:
      - name: param_name
        type: string
        required: true
        description: "What this parameter represents"
    response_hint: "Describe the response shape"
```

2. Build the corresponding read-only API endpoint in the host application
3. Restart the ForteAI server (it loads tool registries on startup)
4. Test via the data mode chat endpoint

### Adding a New Tenant (Application)

1. Create a tenant config: `POST /api/tenants/create`
2. (Optional) Generate an API key for external uploads: `POST /api/tenants/{id}/api-key` with admin Bearer token
3. Upload documentation for that tenant (via admin dashboard or external API)
4. (Optional) Create a tool registry YAML in `backend/tools/{tenant_id}.yaml`
5. Embed the widget in the new app with the tenant ID
