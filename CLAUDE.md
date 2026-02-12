# CLAUDE.md — ForteAI Bot

## Overview

ForteAI is a standalone, multi-tenant AI assistant product with two modes:
- **Help Mode** — RAG over uploaded documentation (Phase 1)
- **Data Mode** — LLM function calling against host app APIs (Phase 2)

## Tech Stack

- **Backend:** Python 3.11+, FastAPI
- **Vector Store:** ChromaDB (embedded)
- **LLM:** OpenAI or Anthropic Claude (configurable per tenant)
- **Widget:** Vanilla JS (no framework dependency)
- **Admin:** HTML + vanilla JS

## Project Structure

```
forteaibot/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # Settings (from .env)
│   │   ├── models/schemas.py    # Pydantic models
│   │   ├── routers/             # API endpoints
│   │   │   ├── chat.py          # Chat (help + data mode)
│   │   │   ├── documents.py     # Document upload/management
│   │   │   ├── tenants.py       # Tenant config
│   │   │   └── analytics.py     # Usage analytics
│   │   ├── services/            # Business logic
│   │   │   ├── rag_engine.py    # ChromaDB + RAG pipeline
│   │   │   ├── query_engine.py  # Function calling engine
│   │   │   ├── llm_service.py   # LLM abstraction layer
│   │   │   └── document_processor.py  # Chunking + parsing
│   │   └── tools/registry.py    # Tool registry loader
│   ├── tools/                   # YAML tool definitions per tenant
│   │   └── chirocloud.yaml
│   ├── requirements.txt
│   └── Dockerfile
├── widget/                      # Embeddable chat widget
├── admin/                       # Admin dashboard
└── docs/DESIGN.md               # Full design document
```

## Commands

```bash
# Setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env   # Edit with your API keys

# Run locally
uvicorn app.main:app --reload --port 8500

# Run with Docker
docker build -t forteai .
docker run -p 8500:8500 forteai
```

## Key Patterns

- **Multi-tenancy:** ForteAI tenant (which app) + App-level tenant (which account)
- **Tool Registry:** YAML files in `backend/tools/` define available data queries per tenant
- **Adding a new data query:** Add entry to the tenant's YAML + build the API endpoint in the host app
- **Adding help content:** Upload via admin dashboard or POST to `/api/documents/upload`

## Code Style

- Python: follow PEP 8
- Use type hints
- Async endpoints where I/O is involved
