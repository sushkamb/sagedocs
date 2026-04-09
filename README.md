# SageDocs

A standalone, multi-tenant AI assistant that can be embedded into any web application. SageDocs provides two capabilities through a single chat widget:

- **Help Mode** — Answers "how do I..." questions by searching uploaded documentation (RAG)
- **Data Mode** — Answers business questions by querying the host application's API (LLM function calling)

SageDocs is application-agnostic. Any app can integrate it by embedding a small JS widget and configuring a tenant. The first integration target is [ChiroCloud](https://chirocloud.com).

## How It Works

```
┌──────────────────────────────────┐
│         Host Application         │
│                                  │
│   ┌──────────────────────────┐   │
│   │   SageDocs Chat Widget    │   │
│   └────────────┬─────────────┘   │
└────────────────┼─────────────────┘
                 │
                 ▼
┌──────────────────────────────────┐
│      SageDocs Service (API)       │
│                                  │
│   Help Mode        Data Mode     │
│   (RAG +           (Function     │
│    ChromaDB)        Calling)     │
│                        │         │
│        LLM Layer       │         │
│   (OpenAI / Claude)    │         │
└────────────────────────┼─────────┘
                         │
                         ▼
               Host Application API
```

**Help Mode:** User asks "How do I submit a claim?" — SageDocs searches the uploaded documentation and generates an answer with source references.

**Data Mode:** User asks "How many new patients this month?" — SageDocs calls the host app's API using function calling and presents the results in natural language.

## Tech Stack

| Component | Technology |
|---|---|
| Backend | Python 3.11+, FastAPI |
| Vector Store | ChromaDB (embedded, self-hosted) |
| LLM | OpenAI GPT-5.2 / Anthropic Claude (configurable) |
| Embeddings | OpenAI text-embedding-3-small |
| Chat Widget | Vanilla JavaScript |
| Admin Dashboard | HTML + vanilla JS |
| Deployment | systemd + Apache on AWS Lightsail |

## Quick Start

### Prerequisites

- Python 3.11 or higher
- An OpenAI API key (or Anthropic API key)

### Setup

```bash
# Clone the repo
git clone <repo-url>
cd sagedocs

# Create virtual environment
cd backend
python -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp ../.env.example .env
# Edit .env and add your API key(s)

# Run the server
uvicorn app.main:app --reload --port 8500
```

### Verify It's Running

- API: http://localhost:8500
- Swagger docs: http://localhost:8500/docs
- Admin dashboard: http://localhost:8500/admin

### Embed the Widget

Add two lines to any web page:

```html
<script src="http://localhost:8500/widget/sagedocs-widget.js"></script>
<script>
  SageDocs.init({
    tenant: 'chirocloud',
    accountNumber: '12345',       // optional — enables data mode
    token: 'user-jwt-token',      // optional — enables data mode
  });
</script>
```

## Project Structure

```
sagedocs/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI entry point
│   │   ├── config.py               # Settings (from .env)
│   │   ├── models/schemas.py       # Pydantic request/response models
│   │   ├── routers/
│   │   │   ├── admin_auth.py       # Admin JWT login/verify
│   │   │   ├── chat.py             # POST /api/chat — main chat endpoint
│   │   │   ├── documents.py        # Document upload, list, delete
│   │   │   ├── external.py         # External API (API key auth)
│   │   │   ├── tenants.py          # Tenant configuration CRUD
│   │   │   └── analytics.py        # Usage tracking and content gaps
│   │   ├── services/
│   │   │   ├── rag_engine.py       # ChromaDB + RAG pipeline
│   │   │   ├── query_engine.py     # Function calling against host APIs
│   │   │   ├── llm_service.py      # OpenAI / Claude abstraction
│   │   │   └── document_processor.py  # PDF, HTML, Markdown parsing + chunking
│   │   └── tools/
│   │       └── registry.py         # YAML tool registry loader
│   ├── tools/
│   │   └── chirocloud.yaml         # ChiroCloud data query tool definitions
│   ├── requirements.txt
├── widget/
│   ├── sagedocs-widget.js           # Embeddable chat widget
│   └── sagedocs-widget.css          # Widget styles
├── admin/
│   ├── index.html                  # Admin dashboard
│   └── login.html                  # Admin login page
├── docs/
│   ├── ARCHITECTURE.md             # Full architecture reference
│   ├── DESIGN.md                   # Design document and roadmap
│   ├── DEPLOYMENT.md               # AWS Lightsail deployment guide
│   └── BUILD_AND_TEST.md           # Build and test guide
├── .env.example                    # Environment variable template
├── .gitignore
├── CLAUDE.md                       # Claude Code development guide
└── README.md                       # This file
```

## Multi-Tenancy

SageDocs supports two levels of tenancy:

1. **SageDocs Tenant** — Which application (e.g., `chirocloud`, `turncloud`). Controls which help docs and tool registry to use.
2. **App-Level Tenant** — Which account within that application (e.g., a specific clinic). Passed through to the host app's API for data scoping.

Help Mode uses only the SageDocs tenant (all clinics share the same docs). Data Mode uses both (each clinic queries their own data).

## API Endpoints

### Public

| Endpoint | Method | Description |
|---|---|---|
| `/api/chat/` | POST | Main chat — auto-routes between help and data mode |
| `/api/chat/help` | POST | Help mode only — answers from documentation |
| `/api/chat/data` | POST | Data mode only — queries host app API |
| `/api/tenants/{id}` | GET | Get tenant configuration (used by widget) |
| `/health` | GET | Health check |

### Admin (requires Bearer token from `/api/admin/login`)

| Endpoint | Method | Description |
|---|---|---|
| `/api/admin/login` | POST | Login with username/password, returns JWT token |
| `/api/admin/verify` | GET | Check if current token is valid |
| `/api/documents/upload` | POST | Upload and index a document |
| `/api/documents/list` | GET | List indexed documents for a tenant |
| `/api/documents/delete` | DELETE | Remove a document from the index |
| `/api/tenants/create` | POST | Create/update tenant configuration |
| `/api/tenants/` | GET | List all tenants |
| `/api/tenants/{id}/api-key` | POST | Generate API key for external uploads |
| `/api/analytics/summary` | GET | Question counts (total, answered, unanswered) |
| `/api/analytics/questions` | GET | List logged questions (filterable) |

### External API (requires `X-API-Key` header)

| Endpoint | Method | Description |
|---|---|---|
| `/api/v1/documents/upload` | POST | Upload document using per-tenant API key |

## Adding a New Host Application

1. **Create a tenant** via the admin dashboard or `POST /api/tenants/create`
2. **Upload help docs** via the admin dashboard or `POST /api/documents/upload`
3. **Add the widget** to your app's HTML with the tenant ID
4. **(Optional) Create a tool registry** YAML file in `backend/tools/{tenant}.yaml` for data mode
5. **(Optional) Build read-only API endpoints** in your host app for the tools to call

## Configuration

All settings are controlled via environment variables (`.env` file). See `.env.example` for the full list:

| Variable | Default | Description |
|---|---|---|
| `LLM_PROVIDER` | `openai` | LLM provider (`openai` or `anthropic`) |
| `LLM_MODEL` | `gpt-5.2` | Primary model for data queries |
| `LLM_MODEL_FAST` | `gpt-5.2-instant` | Fast model for help queries |
| `OPENAI_API_KEY` | — | OpenAI API key |
| `ANTHROPIC_API_KEY` | — | Anthropic API key (if using Claude) |
| `EMBEDDING_MODEL` | `text-embedding-3-small` | Model for document embeddings |
| `CHROMA_PERSIST_DIR` | `./data/chroma` | ChromaDB storage location |
| `PORT` | `8500` | Server port |
| `LOG_LEVEL` | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `CORS_ORIGINS` | `http://localhost` | Allowed CORS origins (comma-separated) |
| `ADMIN_USERNAME` | `admin` | Admin dashboard login username |
| `ADMIN_PASSWORD` | — | Admin dashboard login password |
| `JWT_SECRET` | — | Secret for signing admin JWT tokens |
| `ADMIN_SECRET_KEY` | — | Legacy key for external API key generation |

## Documentation

- [Architecture](docs/ARCHITECTURE.md) — Full architecture reference
- [Design Document](docs/DESIGN.md) — Design document and rollout plan
- [Build and Test Guide](docs/BUILD_AND_TEST.md) — Detailed setup, testing, and deployment instructions
- [Deployment Guide](docs/DEPLOYMENT.md) — AWS Lightsail deployment guide

## License

Proprietary - Forte Software, Inc.
