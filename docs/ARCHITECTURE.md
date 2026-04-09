# SageDocs — Architecture & How It Works

**Date:** 2026-02-11

A complete technical reference for the SageDocs project: what it is, how every piece fits together, and how data flows through the system.

---

## 1. What Is SageDocs?

SageDocs is a standalone, multi-tenant AI assistant that can be embedded into any web application with two lines of JavaScript. It provides two capabilities through a single chat widget:

- **Help Mode** — Answers "how do I..." questions using RAG (Retrieval-Augmented Generation) over uploaded documentation
- **Data Mode** — Answers business/data questions by calling the host application's API via LLM function calling

Think of it as a **smart receptionist**: it has read all the manuals (Help Mode) and can look up information in the company's systems on your behalf (Data Mode).

The first integration target is **ChiroCloud**, but the architecture is application-agnostic.

---

## 2. High-Level Architecture

```
 ┌──────────────────────────────────────────────────────┐
 │              Host App (e.g., ChiroCloud)              │
 │                                                      │
 │   ┌──────────────────────────────────────────────┐   │
 │   │     <script src="sagedocs-widget.js">         │   │
 │   │     SageDocs.init({tenant, token, account})   │   │
 │   └───────────────────┬──────────────────────────┘   │
 └───────────────────────┼──────────────────────────────┘
                         │ HTTP
                         ▼
 ┌──────────────────────────────────────────────────────┐
 │            SageDocs Service (FastAPI :8500)            │
 │                                                      │
 │  ┌────────────┐  ┌─────────────┐  ┌──────────────┐  │
 │  │ Chat Router │  │  Documents  │  │  Analytics   │  │
 │  │ /api/chat/* │  │  /api/docs  │  │  /api/stats  │  │
 │  └──────┬─────┘  └──────┬──────┘  └──────────────┘  │
 │         │               │                            │
 │  ┌──────┴───────────────┴───────┐                    │
 │  │         Services Layer       │                    │
 │  │                              │                    │
 │  │  ┌───────────┐ ┌──────────┐ │  ┌──────────────┐  │
 │  │  │RAG Engine │ │  Query   │ │  │  LLM Service │  │
 │  │  │(Help Mode)│ │  Engine  │ │  │ OpenAI/Claude│  │
 │  │  │           │ │(Data Mode│ │  │              │  │
 │  │  └─────┬─────┘ └────┬────┘ │  └──────────────┘  │
 │  └────────┼────────────┼──────┘                     │
 └───────────┼────────────┼────────────────────────────┘
             │            │
      ┌──────┴──┐   ┌─────┴──────────┐
      │ChromaDB │   │ Host App API   │
      │(vectors)│   │/api/assistant/*│
      └─────────┘   └────────────────┘
```

---

## 3. Tech Stack

| Component | Technology |
|---|---|
| Backend API | Python 3.11+, FastAPI |
| Vector Store | ChromaDB (embedded) |
| LLM | OpenAI or Anthropic Claude (configurable) |
| Embeddings | OpenAI `text-embedding-3-small` |
| Chat Widget | Vanilla JS (zero framework dependencies) |
| Admin Dashboard | HTML + vanilla JS |
| Deployment | systemd + Apache on AWS Lightsail |

---

## 4. Project Structure

```
sagedocs/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI entry point, CORS, static mounts
│   │   ├── config.py                # Pydantic settings (reads .env)
│   │   ├── models/
│   │   │   └── schemas.py           # Request/response Pydantic models
│   │   ├── auth.py                    # API key verification dependency (external API)
│   │   ├── routers/
│   │   │   ├── admin_auth.py        # Admin JWT login/verify + verify_admin_token dependency
│   │   │   ├── chat.py              # POST /api/chat/* — main chat logic
│   │   │   ├── documents.py         # Document upload/list/delete (admin JWT protected)
│   │   │   ├── external.py          # External API (authenticated uploads via API key)
│   │   │   ├── tenants.py           # Tenant CRUD + API key generation (admin JWT protected)
│   │   │   └── analytics.py         # Usage logging & summaries (admin JWT protected)
│   │   ├── services/
│   │   │   ├── rag_engine.py        # ChromaDB + RAG pipeline
│   │   │   ├── query_engine.py      # Function calling engine
│   │   │   ├── llm_service.py       # LLM abstraction (OpenAI/Anthropic)
│   │   │   └── document_processor.py # PDF/HTML parsing, chunking, images
│   │   └── tools/
│   │       └── registry.py          # YAML tool registry loader
│   ├── tools/
│   │   └── chirocloud.yaml          # Tool definitions for ChiroCloud
│   ├── requirements.txt
├── widget/
│   ├── sagedocs-widget.js            # Embeddable chat widget
│   └── sagedocs-widget.css           # Widget styles
├── admin/
│   ├── index.html                   # Admin dashboard (single-page)
│   ├── login.html                   # Admin login page
│   └── test-widget.html             # Widget test page
├── docs/
│   ├── DESIGN.md                    # Design document & roadmap
│   ├── BUILD_AND_TEST.md            # Setup, testing, deployment guide
│   └── ARCHITECTURE.md              # This file
├── .env.example                     # Environment variable template
├── CLAUDE.md                        # AI assistant instructions
└── README.md                        # Quick start
```

---

## 5. Multi-Tenancy Model

SageDocs has **two levels** of tenancy:

| Level | Example | Purpose |
|---|---|---|
| **SageDocs Tenant** | `"chirocloud"` | Identifies which app — determines docs, tools, and settings |
| **App Account** | `"clinic_001"` | Identifies which account within the app — scopes data queries |

### How It Works

- **Help Mode** uses the SageDocs tenant only. All clinics using ChiroCloud share the same help documentation.
- **Data Mode** uses both. The account number is passed as a header to the host app's API, which handles its own schema/data routing.

### Data Isolation

- ChromaDB collections are named `tenant_{tenant_id}` — no cross-tenant document leakage
- Analytics are logged per tenant in separate JSONL files
- Tool registries are loaded per tenant from separate YAML files
- Host app data is scoped by the account number header — SageDocs never stores or caches it

---

## 6. Help Mode (RAG Pipeline)

### 6.1 Document Ingestion

```
Admin uploads PDF/HTML/MD
         │
         ▼
 Document Processor (document_processor.py)
    ├── Extract text (PyMuPDF for PDF, BeautifulSoup for HTML)
    ├── Extract images (skip < 2KB or < 80x80px)
    ├── Describe images via LLM vision model
    ├── Embed descriptions as [Screenshot: filename | description]
    └── Chunk text (800 tokens, 200 token overlap)
         │
         ▼
 ChromaDB (rag_engine.py)
    ├── Embed each chunk via OpenAI embeddings
    ├── Store in collection: tenant_{tenant_id}
    └── Metadata: tenant, title, filename, chunk_index, uploaded_at
```

**Key details:**
- Uses `RecursiveCharacterTextSplitter` with separators: paragraphs, sentences, then words
- Images are saved to `/data/images/{tenant}/img_{uuid}.{ext}` on disk
- Image descriptions are baked into chunk text so they participate in semantic search
- Re-uploading a document deletes old chunks first (no stale content)

### 6.2 Query Pipeline

```
User: "How do I submit a claim?"
         │
         ▼
 1. Embed the question (OpenAI text-embedding-3-small)
 2. Semantic search in ChromaDB → top 5 matching chunks
 3. Extract image filenames from chunks via regex
 4. Build LLM prompt:
    System: "Answer using ONLY the provided documentation.
             If the answer isn't in the docs, say so clearly."
    Context: [top 5 chunks]
    User: "How do I submit a claim?"
 5. LLM generates answer (uses fast model to minimize cost)
         │
         ▼
 Response:
   {
     reply: "To submit a claim: 1. Open the patient's visit...",
     sources: [{title: "Claims Guide", filename: "claims.pdf", chunk_index: 2}],
     images: ["/data/images/chirocloud/img_xyz.png"]
   }
```

---

## 7. Data Mode (Function Calling)

### 7.1 Tool Registry

Each tenant has a YAML file (`backend/tools/{tenant}.yaml`) that defines what data queries the LLM can make. Example:

```yaml
base_url: https://my.turncloud.com:4132

tools:
  - name: get_patient_count
    description: "Get the number of patients for a date range"
    endpoint: /api/Assistant/GetPatientCount
    method: GET
    parameters:
      - name: date_from
        type: string
        required: true
        description: "Start date (YYYY-MM-DD)"
      - name: date_to
        type: string
        required: true
        description: "End date (YYYY-MM-DD)"
      - name: status
        type: string
        required: false
        enum: [new, active, inactive]
        description: "Patient status filter"
    response_hint: "Returns { count: number }"
```

### 7.2 Available ChiroCloud Tools

| Tool | Purpose | Example Question |
|---|---|---|
| `get_patient_count` | Count patients in date range by status | "How many new patients this month?" |
| `get_appointments_today` | Today's appointment count and list | "How many patients scheduled today?" |
| `get_aging_claims` | Unpaid claims by aging bucket | "What claims are past 90 days?" |
| `get_provider_schedule` | Doctor's appointments for a date | "What's Dr. Smith's schedule Friday?" |
| `get_patient_birthdays` | Patient birthdays in date range | "Any patient birthdays this week?" |
| `get_collection_summary` | Payment collection stats | "How much did we collect this month?" |
| `get_open_balances` | Outstanding patient balances | "Which patients owe money?" |
| `search_patient` | Search by name, get next appointment | "Look up John Smith" |

### 7.3 Query Flow

```
User: "How many new patients this month?"
         │
         ▼
 1. Load tools from backend/tools/chirocloud.yaml
 2. Convert YAML → OpenAI function-calling format
         │
         ▼
 FIRST LLM CALL (tool selection):
   System: "You are a data assistant. Use the available tools."
   Tools: [get_patient_count, get_aging_claims, ...]
   User: "How many new patients this month?"
   → LLM picks: get_patient_count(date_from="2026-02-01", date_to="2026-02-11", status="new")
         │
         ▼
 EXECUTE API CALL:
   GET https://my.turncloud.com:4132/api/Assistant/GetPatientCount
     ?date_from=2026-02-01&date_to=2026-02-11&status=new
   Headers:
     Authorization: Bearer {user's JWT}
     X-Account-Number: clinic_001
   → Response: { count: 14 }
         │
         ▼
 SECOND LLM CALL (format results):
   System: "Format these results into a clear answer"
   Context: { count: 14 }
   → "You've had 14 new patients so far in February."
         │
         ▼
 Response:
   { reply: "You've had 14 new patients so far in February.", sources: [] }
```

---

## 8. Chat Router Logic

The main `/api/chat/` endpoint auto-routes between modes:

```
POST /api/chat/
  │
  ├─ Has account_number + token?
  │    YES → Try help mode first (RAG search)
  │    │      ├─ Found relevant docs? → Return help answer
  │    │      └─ No docs matched?     → Fall back to data mode (function calling)
  │    │
  │    NO  → Help mode only (RAG search)
  │
  └─ Log question to analytics (tenant, question, answered/unanswered)
```

There are also dedicated endpoints:
- `POST /api/chat/help` — Forces help mode only
- `POST /api/chat/data` — Forces data mode only

---

## 9. API Reference

### Chat Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/chat/` | POST | Main chat — auto-routes help then data |
| `/api/chat/help` | POST | Help mode only (RAG) |
| `/api/chat/data` | POST | Data mode only (function calling) |

**Request body (`ChatRequest`):**

```json
{
  "tenant": "chirocloud",
  "message": "How do I submit a claim?",
  "account_number": "clinic_001",   // optional, required for data mode
  "token": "jwt_xyz",               // optional, required for data mode
  "session_id": "uuid"              // optional, for session continuity
}
```

**Response body (`ChatResponse`):**

```json
{
  "reply": "To submit a claim: ...",
  "sources": [
    { "title": "Claims Guide", "filename": "claims.pdf", "chunk_index": 2 }
  ],
  "images": ["/data/images/chirocloud/img_xyz.png"],
  "session_id": "generated-uuid"
}
```

### Admin Auth Endpoints

| Endpoint | Method | Auth | Purpose |
|---|---|---|---|
| `/api/admin/login` | POST | None | Login with username/password, returns JWT token |
| `/api/admin/verify` | GET | Bearer token | Check if current token is still valid |

**Login request:**

```json
{
  "username": "admin",
  "password": "your-password"
}
```

**Login response:**

```json
{
  "token": "eyJ...",
  "expires_in": 86400
}
```

### Document Endpoints

All document endpoints require `Authorization: Bearer <token>` header (obtained from `/api/admin/login`).

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/documents/upload` | POST | Upload file, chunk, embed, index (admin/internal) |
| `/api/documents/list` | GET | List indexed docs for a tenant |
| `/api/documents/delete` | DELETE | Remove document from index |

### External API Endpoints

| Endpoint | Method | Auth | Purpose |
|---|---|---|---|
| `/api/v1/documents/upload` | POST | `X-API-Key` header | Authenticated document upload for external services |

The tenant is derived from the API key — callers cannot upload to a different tenant. See [External Document Upload API](#external-document-upload-api) below for details.

### Tenant Endpoints

All write endpoints require `Authorization: Bearer <token>` header. `GET /api/tenants/{id}` is public (used by the widget).

| Endpoint | Method | Auth | Purpose |
|---|---|---|---|
| `/api/tenants/create` | POST | Bearer token | Create or update tenant config |
| `/api/tenants/{id}` | GET | None (public) | Get tenant config |
| `/api/tenants/{id}/api-key` | POST | Bearer token | Generate API key for external uploads |
| `/api/tenants/` | GET | Bearer token | List all tenants |

**Tenant config includes:** welcome message, placeholder text, starter questions, widget colors, logo URL, position (bottom-right/bottom-left), LLM model override, help/data mode toggles.

### Analytics Endpoints

All analytics endpoints require `Authorization: Bearer <token>` header.

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/analytics/questions` | GET | List logged questions (filter by unanswered) |
| `/api/analytics/summary` | GET | Counts: total, answered, unanswered |

---

## 10. Core Services

### 10.1 LLM Service (`services/llm_service.py`)

Abstraction layer over OpenAI and Anthropic APIs.

| Method | Purpose |
|---|---|
| `chat(system_prompt, user_message, tools)` | Chat completion with optional tool calling |
| `get_embedding(text)` | Generate text embedding (always uses OpenAI) |
| `describe_image(image_bytes, context)` | Vision model for image descriptions |

- Provider is configurable via `LLM_PROVIDER` env var (`openai` or `anthropic`)
- Converts OpenAI tool format to Anthropic format transparently
- Help mode uses the fast/cheap model (`LLM_MODEL_FAST`)
- Data mode uses the primary model (`LLM_MODEL`)

### 10.2 RAG Engine (`services/rag_engine.py`)

Manages ChromaDB and the full help-mode pipeline.

| Method | Purpose |
|---|---|
| `ingest_document(file_path, title, tenant)` | Chunk, embed, store in ChromaDB |
| `query(tenant, question, top_k=5)` | Semantic search + LLM answer |
| `delete_document(tenant, filename)` | Remove chunks for a document |
| `get_document_list(tenant)` | List indexed docs with chunk counts |

### 10.3 Query Engine (`services/query_engine.py`)

Handles data-mode function calling against host app APIs.

| Method | Purpose |
|---|---|
| `query(tenant, question, account_number, token, base_url)` | Full function-calling flow |
| `_get_openai_tools(tenant)` | Convert YAML registry to OpenAI tool format |
| `_call_api(base_url, endpoint, method, params, account_number, token)` | Execute authenticated API call |

### 10.4 Document Processor (`services/document_processor.py`)

Parses uploaded files into chunks ready for embedding.

| Method | Purpose |
|---|---|
| `process_file(file_path, title, tenant)` | Full extraction + chunking pipeline |
| `_extract_pdf(file_path)` | PyMuPDF text + image extraction |
| `_extract_html(file_path)` | BeautifulSoup HTML parsing |
| `_extract_text(file_path)` | Plain text / Markdown |

---

## 11. Widget (`widget/sagedocs-widget.js`)

### Integration

```html
<script src="https://sagedocs.yourdomain.com/widget/sagedocs-widget.js"></script>
<script>
  SageDocs.init({
    tenant: 'chirocloud',
    accountNumber: '12345',       // optional — enables data mode
    token: '{jwt}',               // optional — enables data mode
    theme: 'light',               // or 'dark'
    position: 'bottom-right',     // or 'bottom-left'
    apiUrl: 'https://sagedocs.yourdomain.com'
  });
</script>
```

### Features

- **Floating action button (FAB)** — Chat bubble toggles the panel
- **Chat panel** — 380px wide, 520px tall
- **Session history** — Persisted in browser localStorage across page reloads
- **Typing indicator** — Animated dots while waiting for response
- **Markdown rendering** — Bold, italic, code blocks, lists
- **Image display** — Inline images with fullscreen modal on click
- **Source attribution** — Clickable source references for help-mode answers
- **Starter questions** — Clickable suggestions loaded from tenant config
- **Responsive** — Full screen on mobile (with margins)

### Initialization Flow

1. Fetches `/api/tenants/{tenant}` for custom welcome message, placeholder, starter questions
2. Renders FAB and collapsed panel
3. On user message: POSTs to `/api/chat/` with tenant, message, account, token
4. Receives `{reply, sources, images, session_id}` and renders the response

---

## 12. Admin Dashboard (`admin/index.html`)

A single-page admin interface with four tabs:

### Documents Tab
- Upload PDF, HTML, Markdown, or TXT files
- Select tenant and provide a descriptive title
- View indexed documents with chunk counts
- Delete documents (removes from ChromaDB)

### Test Chat Tab
- Live chat interface against current indexed docs
- Test answers before users see them
- Shows sources and images in responses
- Implementation note: this tab embeds the actual `sagedocs-widget.js` in **inline mode** (`SageDocs.init({ inline: true, target: '#testChatHost', ... })`) so admins see the exact rendering, markdown handling, and behavior end users will get. There is no separate admin chat code path.

### Analytics Tab
- Total questions asked
- Percentage answered vs. unanswered
- List of unanswered questions — the most valuable feature for identifying documentation gaps

### Settings Tab
- Tenant configuration: welcome message, colors, logo
- LLM model override per tenant
- System prompt customization
- Help/Data mode toggles
- Widget position and starter questions

---

## 13. Configuration

### Environment Variables (`.env`)

```
# LLM Configuration
LLM_PROVIDER=openai              # "openai" or "anthropic"
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
LLM_MODEL=gpt-5.2               # Primary model (data mode)
LLM_MODEL_FAST=gpt-5-mini       # Fast model (help mode, cheaper)
EMBEDDING_MODEL=text-embedding-3-small

# Storage
CHROMA_PERSIST_DIR=./data/chroma

# Logging
LOG_LEVEL=INFO                   # DEBUG, INFO, WARNING, ERROR

# Server
HOST=0.0.0.0
PORT=8500
CORS_ORIGINS=http://localhost,https://chirocloud.com

# Admin
ADMIN_SECRET_KEY=your-random-string    # Protects external API key generation
ADMIN_USERNAME=admin                   # Admin dashboard login username
ADMIN_PASSWORD=change-this-password    # Admin dashboard login password
JWT_SECRET=change-this-jwt-secret      # Secret for signing admin JWT tokens
```

### Static Mounts

| URL Path | Serves |
|---|---|
| `/widget` | `sagedocs-widget.js` and `.css` |
| `/admin` | Admin dashboard HTML |
| `/data/images` | Extracted images from documents |
| `/docs` | Swagger API docs (auto-generated by FastAPI) |

---

## 14. Security Model

### External Document Upload API

SageDocs provides an authenticated external API (`POST /api/v1/documents/upload`) that allows external services to programmatically upload documents. Authentication uses per-tenant API keys.

**Generating an API key:**

First, obtain a JWT token by logging in:

```bash
curl -X POST http://localhost:8500/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your-password"}'
# → { "token": "eyJ...", "expires_in": 86400 }
```

Then use the token to generate an API key:

```bash
curl -X POST http://localhost:8500/api/tenants/chirocloud/api-key \
  -H "Authorization: Bearer <jwt_token>"
# → { "tenant_id": "chirocloud", "api_key": "fai_...", "message": "Save this key now..." }
```

The plaintext key is returned **once** — it cannot be retrieved again. Only the SHA-256 hash is stored in the tenant config.

**Uploading a document:**

```bash
curl -X POST http://localhost:8500/api/v1/documents/upload \
  -H "X-API-Key: fai_<generated_key>" \
  -F "file=@document.pdf" \
  -F "title=My Document"
# → { "success": true, "message": "...", "filename": "document.pdf", "chunk_count": 12 }
```

The tenant is derived from the API key — callers cannot upload to a different tenant.

### No Direct Database Access

The LLM **never generates SQL** and **never touches a database**. It can only call pre-defined API endpoints listed in the YAML tool registry. This eliminates an entire class of injection attacks.

### JWT Passthrough

SageDocs forwards the user's JWT and account number as HTTP headers to the host app. It never validates or decodes them — the host app is responsible for authentication and authorization.

```
Widget → SageDocs → Host App API
  token → passed through → validated here
  account_number → passed as header → used for schema routing
```

### Read-Only Endpoints

All host app endpoints under `/api/assistant/*` are strictly GET/read-only. The LLM cannot modify data.

### API Key Authentication

The external document upload API uses per-tenant API keys:

- Keys are generated via `POST /api/tenants/{id}/api-key`, protected by admin JWT authentication
- Keys use a `fai_` prefix followed by a `secrets.token_urlsafe(32)` token
- Only the SHA-256 hash of the key is stored in the tenant JSON config
- The plaintext key is returned once at generation time and cannot be retrieved
- On each request, the provided key is hashed and compared against all tenant configs to identify the tenant

### CORS Control

The `CORS_ORIGINS` environment variable restricts which domains can embed the widget and call the API.

### No Cross-Tenant Data

- Help docs scoped per tenant in ChromaDB collections
- Data queries scoped per account via host app headers
- SageDocs never stores or caches host app data

---

## 15. Data Flow Summary

### Help Mode End-to-End

```
1. Admin uploads PDF
2. → Document Processor extracts text + images, creates chunks
3. → Chunks embedded and stored in ChromaDB

4. User asks "How do I..."
5. → Widget POSTs to /api/chat/help
6. → RAG Engine: embed question, search top-5 chunks
7. → LLM generates answer from documentation context
8. → Widget renders answer + sources + images
```

### Data Mode End-to-End

```
1. Admin creates tool registry YAML
2. Host app builds /api/assistant/* endpoints

3. User asks "How many new patients..."
4. → Widget POSTs to /api/chat/data (with JWT + account)
5. → Query Engine loads YAML tools
6. → First LLM call: selects tool + parameters
7. → Executes API call to host app with auth headers
8. → Second LLM call: formats results into natural language
9. → Widget displays answer
```

---

## 16. Adding a New Integration

To connect SageDocs to a new host application:

1. **Create a tenant** — via `POST /api/tenants/create` or the admin Settings tab
2. **Upload help docs** — PDF, HTML, or Markdown via admin Documents tab
3. **Write a tool registry** — Create `backend/tools/{tenant_id}.yaml` with available data queries
4. **Build API endpoints** — Add read-only `/api/assistant/*` endpoints in the host app
5. **Embed the widget** — Add the 2-line JS snippet to the host app's HTML
6. **Configure** — Set welcome message, colors, starter questions via admin
7. **Test** — Use admin Test Chat and the widget test page
8. **Monitor** — Check analytics for unanswered questions to identify content gaps

---

## 17. Adding a New Data Query Tool

1. Add the tool definition to `backend/tools/{tenant}.yaml`:

```yaml
  - name: get_new_metric
    description: "Description the LLM uses to decide when to call this"
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
3. Restart the SageDocs server (tool registries are loaded on startup)
4. Test by asking a natural language question that should trigger the new tool

---

## 18. Key Design Decisions

| Decision | Rationale |
|---|---|
| **No SQL generation** | Eliminates injection risks; LLM constrained to pre-approved endpoints |
| **YAML tool registry** | Easy to add new queries without code changes; human-readable |
| **Two LLM calls for data mode** | First selects the tool, second formats results — cleaner separation |
| **Fast model for help mode** | Help answers are simpler; saves cost without quality loss |
| **ChromaDB embedded** | No separate database server needed; persists to disk |
| **Vanilla JS widget** | Zero framework dependency; embeds anywhere without conflicts |
| **JWT passthrough** | SageDocs doesn't need to understand auth — host app handles it |
| **Per-tenant ChromaDB collections** | Clean isolation; easy to delete/rebuild per tenant |
| **Image extraction + vision descriptions** | Screenshots in docs become searchable and referenceable in answers |
| **Analytics logging** | Unanswered questions become the documentation roadmap |

---

## 19. File-by-File Reference

| File | Purpose |
|---|---|
| `backend/app/main.py` | FastAPI app initialization, CORS, logging setup, static mounts, root health check |
| `backend/app/config.py` | Pydantic `Settings` class, reads `.env` |
| `backend/app/auth.py` | API key verification dependency for external endpoints |
| `backend/app/models/schemas.py` | `ChatRequest`, `ChatResponse`, `TenantConfig`, etc. |
| `backend/app/routers/admin_auth.py` | Admin JWT login/verify endpoints + `verify_admin_token` dependency |
| `backend/app/routers/chat.py` | Chat endpoints: `/`, `/help`, `/data` with auto-routing logic |
| `backend/app/routers/documents.py` | Upload, list, delete documents + shared `process_upload()` (admin JWT protected) |
| `backend/app/routers/external.py` | External API: authenticated document upload via API key |
| `backend/app/routers/tenants.py` | Tenant CRUD + API key generation endpoints (admin JWT protected) |
| `backend/app/routers/analytics.py` | Question logging and summary stats (admin JWT protected) |
| `backend/app/services/rag_engine.py` | ChromaDB management, embedding, semantic search, answer generation |
| `backend/app/services/query_engine.py` | YAML loading, LLM function calling, API execution |
| `backend/app/services/llm_service.py` | OpenAI/Anthropic abstraction, chat, embeddings, vision |
| `backend/app/services/document_processor.py` | File parsing, image extraction, text chunking |
| `backend/app/tools/registry.py` | Utility to load and validate YAML tool registries |
| `backend/tools/chirocloud.yaml` | ChiroCloud tool definitions (8 tools) |
| `widget/sagedocs-widget.js` | Embeddable chat widget with FAB, chat panel, markdown rendering. Supports floating mode (default) and `inline` mode for embedding inside a host element (used by the admin Test Chat). |
| `widget/sagedocs-widget.css` | Widget styles, responsive layout, light/dark themes |
| `admin/index.html` | Admin dashboard: docs, test chat, analytics, settings |
| `admin/login.html` | Admin login page (username/password → JWT token) |
| `admin/test-widget.html` | Standalone widget test page |
