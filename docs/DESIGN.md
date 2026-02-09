# ForteAI Bot — Design Document

**Date:** 2026-02-09
**Status:** Draft
**Author:** Forte Development Team

---

## 1. Overview

ForteAI is a standalone, multi-tenant AI assistant product that provides two capabilities:

1. **Help Mode** — Answers "how do I..." questions using RAG over uploaded documentation
2. **Data Mode** — Answers business/data questions by calling the host application's API via LLM function calling

ForteAI is designed to be application-agnostic. Any application can integrate it by embedding a JS widget and configuring a tenant. The first integration target is **ChiroCloud**.

---

## 2. Goals

- Reduce support burden by letting users self-serve "how do I..." questions
- Give front desk/admin staff conversational access to clinic data
- Build once, reuse across multiple Forte applications
- Keep ForteAI completely separate from host application codebases

---

## 3. Architecture

### 3.1 High-Level Components

```
┌─────────────────────────────────────────────┐
│              Host App (ChiroCloud)           │
│                                             │
│   ┌───────────────────────────────────┐     │
│   │  ForteAI Widget  (JS snippet)     │     │
│   │  - Chat UI                        │     │
│   │  - Passes tenant ID + JWT         │     │
│   └──────────────┬────────────────────┘     │
└──────────────────┼──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│         ForteAI Service (FastAPI)           │
│                                             │
│  ┌─────────────┐    ┌──────────────────┐   │
│  │  RAG Engine  │    │  Query Engine    │   │
│  │  (ChromaDB)  │    │  (Tool Registry) │   │
│  └──────┬──────┘    └────────┬─────────┘   │
│         │                    │              │
│         ▼                    ▼              │
│  ┌─────────────┐    ┌──────────────────┐   │
│  │  Doc Store   │    │  API Proxy       │   │
│  │  per tenant  │    │  (forwards JWT)  │   │
│  └─────────────┘    └────────┬─────────┘   │
│                              │              │
│  ┌─────────────────────────────────────┐   │
│  │  Admin Dashboard                    │   │
│  │  - Doc management, Analytics,       │   │
│  │    Tool config, Widget settings     │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │  LLM Layer (OpenAI / Claude API)    │   │
│  └─────────────────────────────────────┘   │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│       Host App API (e.g. ChiroCloud)        │
│  + Read-only /api/assistant/* endpoints     │
└─────────────────────────────────────────────┘
```

### 3.2 Tech Stack

| Component | Technology |
|---|---|
| Backend API | Python 3.11+, FastAPI |
| Vector Store | ChromaDB (embedded/self-hosted) |
| LLM | OpenAI API or Anthropic Claude API (configurable per tenant) |
| Embeddings | OpenAI text-embedding-3-small |
| Chat Widget | Vanilla JS (no framework dependency) |
| Admin Dashboard | HTML + minimal JS (or React if needed later) |
| Deployment | Docker container on AWS EC2 |

### 3.3 Multi-Tenancy Model

Two levels of tenancy:

1. **ForteAI Tenant** — Which application (e.g., `chirocloud`, `turncloud`, future apps)
2. **App-Level Tenant** — Which account within that application (e.g., ChiroCloud clinic account number)

**Help Mode** uses ForteAI tenant only — all clinics using ChiroCloud share the same help docs.

**Data Mode** uses both — the account number is passed to the host app's API, which handles its own schema/data routing.

---

## 4. Phase 1: Help Mode (RAG)

### 4.1 Document Ingestion Pipeline

1. Admin uploads a file (PDF, HTML, or Markdown) via the dashboard, tagged to a ForteAI tenant
2. **Chunking** — File is split into overlapping chunks (~500-800 tokens each)
3. **Embedding** — Each chunk is converted to a vector using the embedding model
4. **Storage** — Chunks + vectors stored in ChromaDB under the tenant's collection
5. Metadata preserved: title, source file, upload date, chunk index

### 4.2 Query Pipeline (RAG)

1. User types a question in the widget
2. Widget sends the question + tenant ID to the ForteAI API
3. Question is embedded using the same embedding model
4. ChromaDB returns the top 3-5 most relevant chunks from that tenant's collection
5. Retrieved chunks are injected into an LLM prompt:
   > "Answer the user's question using ONLY the following documentation. If the answer isn't in the docs, say you don't know."
6. LLM generates the answer and returns it to the widget
7. Source references are included so users can click through to full documents

### 4.3 Content Refresh

When a document is re-uploaded:
- Old chunks for that file are deleted from ChromaDB
- New chunks replace them
- No stale content remains

---

## 5. Phase 2: Data Mode (Function Calling)

### 5.1 Tool Registry

A YAML configuration file defines available data tools per ForteAI tenant. The LLM sees these as callable functions.

Example (`tools/chirocloud.yaml`):

```yaml
tools:
  - name: get_patient_count
    description: "Get the number of patients for a date range, optionally filtered by status"
    endpoint: /api/assistant/patients/count
    method: GET
    parameters:
      - name: date_from
        type: date
        required: true
        description: "Start date"
      - name: date_to
        type: date
        required: true
        description: "End date"
      - name: status
        type: string
        required: false
        enum: [new, active, inactive]
        description: "Patient status filter"
    response_hint: "Returns { count: number }"

  - name: get_aging_claims
    description: "Get unpaid insurance claims grouped by aging buckets"
    endpoint: /api/assistant/claims/aging
    method: GET
    parameters:
      - name: payer_name
        type: string
        required: false
        description: "Filter by insurance company name"
    response_hint: "Returns array of { bucket, count, total_amount }"

  - name: get_provider_schedule
    description: "Get a doctor's appointments for a specific date"
    endpoint: /api/assistant/schedule
    method: GET
    parameters:
      - name: doctor_name
        type: string
        required: true
      - name: date
        type: date
        required: true
    response_hint: "Returns array of { time, patient_name, visit_type, status }"
```

### 5.2 Query Flow

1. User types: "How many new patients this month?"
2. Widget sends question + tenant ID + account number + JWT to ForteAI API
3. LLM sees the question + tool catalog
4. LLM selects `get_patient_count` with parameters `{ date_from: "2026-02-01", date_to: "2026-02-09", status: "new" }`
5. ForteAI calls ChiroCloud API at `/api/assistant/patients/count` with the user's JWT and account number
6. ChiroCloud API handles tenant scoping (schema routing via account number) and returns `{ count: 14 }`
7. LLM responds: "You've had 14 new patients so far in February."

### 5.3 Starter Tool Set

| Tool | Example Questions |
|---|---|
| `get_patient_count` | "How many new patients this month?" |
| `get_appointments_today` | "How many patients scheduled today?" |
| `get_aging_claims` | "What claims are past 90 days?" |
| `get_provider_schedule` | "What's Dr. Smith's schedule Friday?" |
| `get_patient_birthdays` | "Any patient birthdays this week?" |
| `get_collection_summary` | "How much did we collect this month?" |
| `get_open_balances` | "Which patients have outstanding balances?" |
| `search_patient` | "Look up John Smith's next appointment" |

### 5.4 Security

- **No direct database access** — The LLM never generates SQL or touches a database
- **Function calling only** — The LLM can only call tools explicitly defined in the registry
- **JWT passthrough** — All data requests use the user's existing auth token
- **Account number scoping** — Every data-mode API call includes the account number; ChiroCloud's API handles schema routing
- **Read-only endpoints** — The `/api/assistant/*` endpoints in ChiroCloud are strictly GET/read-only
- **No cross-tenant data leakage** — ForteAI never stores or caches host app data

---

## 6. Embeddable Chat Widget

### 6.1 Integration

Two lines in any host app:

```html
<script src="https://forteai.yourdomain.com/widget/forteai-widget.js"></script>
<script>
  ForteAI.init({
    tenant: 'chirocloud',
    accountNumber: '12345',
    token: '{jwt}',
    theme: 'light'
  });
</script>
```

### 6.2 Features

- Floating chat bubble (configurable position)
- Chat panel with session-based conversation history (stored in browser)
- Streamed responses from the LLM
- Source references for help-mode answers
- Suggested starter questions

### 6.3 Tenant-Configurable Options

- Widget colors and logo (matches host app branding)
- Welcome message
- Input placeholder text
- Position (bottom-right, bottom-left)
- Starter questions
- Help-only mode, Data-only mode, or both

---

## 7. Admin Dashboard

### 7.1 Pages

1. **Documents** — Upload, list, delete help documents per tenant. Shows chunk count and last indexed date.
2. **Test Chat** — Live chat panel to test the bot against current documents before users see it.
3. **Analytics** — Questions per day, most common questions, unanswered questions (content gaps).
4. **Settings** — Widget appearance, LLM model/API key, system prompt customization.
5. **Tools** (Phase 2) — View and manage the tool registry for data-mode integrations.

### 7.2 Analytics — Unanswered Questions

The most valuable feature for sparse documentation: logs every question the bot couldn't answer. This becomes the documentation roadmap — users tell you exactly what help content to write next.

---

## 8. Rollout Plan

| Phase | Scope | Touchpoints with ChiroCloud |
|---|---|---|
| **Phase 1** | Help mode: RAG, widget, admin dashboard | Add one `<script>` tag to ChiroCloud HTML |
| **Phase 2** | Data mode: Tool registry, query engine | Add read-only `/api/assistant/*` endpoints |
| **Phase 3** | Polish: Analytics insights, multi-app onboarding | None |

---

## 9. Future Considerations

- **Conversation memory** — Store chat history server-side for context across sessions
- **Role-based content** — Show different help content based on user role (admin vs front desk vs provider)
- **Proactive suggestions** — Widget detects the current screen and suggests relevant help topics
- **Feedback loop** — Users can thumbs-up/down answers; low-rated answers get flagged for review
- **Multiple LLM providers** — Already abstracted; tenants can choose OpenAI, Claude, or others
