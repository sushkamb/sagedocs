# ChiroCloud Documentation Pipeline Design

## Goal

Systematically create markdown help documentation for ChiroCloud (TurnCloud) that the SageDocs can ingest via RAG to answer user questions. Start with core modules, expand later.

## Current State

- One small help file exists: `backend/uploads/chirocloud/chirocloud-help.md` (47 lines, 5 topics)
- SageDocs RAG pipeline already supports markdown ingestion with chunking and semantic search
- Analytics show 31 logged questions, many unanswered — indicating documentation gaps
- ChiroCloud is a full chiropractic practice management system with 25+ sub-modules

## App Module Map (Discovered via Live Exploration)

| Area | Modules |
|------|---------|
| Main Tabs | Home, Patients, Calendar, Financials, Reports, Administration, Tools, Patient Chat |
| Financials | Claims, Statements, Bulk Payments, Messages |
| Reports | Search Report Generator, Transaction Report, Daysheet, Billing History, EHR Reports, Appointments, Outstanding Claims |
| Administration | General (Clinic Setup, Static Forms), Users & Security, Application Lists, Visits/EHR, Calendar Settings, Ledger Settings, Billing Settings, Reports |
| Tools | Bulk SMS Messaging |
| Patient Chart | Overview, Demographics, Employer, Insurance, Patient History, Cases, Visits/EHR, Ledger (Edit Posting, Charges, Payments, Legacy Postings), Record Center |
| Quick Actions | Appointments, Patient Search, Contact Patient, Statement, Patient Portal, Claim |

## Approach: Capture-then-Write Pipeline

### Phase 1: Capture (Sequential, Single Agent)

Browse every core module in the live app. For each module:

1. Navigate to the screen
2. Capture an accessibility snapshot (structured DOM tree) to `docs/captures/{module}.md`
3. Take a screenshot to `docs/captures/{module}.png`
4. Note key fields, buttons, labels, and workflows

**Output:** A `docs/captures/` directory with raw data files for each module.

### Phase 2: Write (Parallel, Agent Team)

Spawn 3-4 documentation-writer agents, each assigned a module group:

| Agent | Modules | Output Files |
|-------|---------|--------------|
| Agent 1: Patient Management | Patient Lookup, Add New Patient, Patient Search, Demographics | `patients.md` |
| Agent 2: Patient Chart | Overview, Insurance, Cases, Patient History, Record Center | `patient-chart.md` |
| Agent 3: Scheduling | Calendar (Day/Week/Agenda), Booking Appointments, Room Management | `scheduling.md` |
| Agent 4: Billing & Finance | Ledger, Charges, Payments, Claims, Statements, Reports | `billing-and-finance.md` |

Each agent reads captured snapshots and writes polished markdown documentation following a consistent template.

### Phase 3: Review & Upload (Sequential)

1. Review all generated docs for accuracy and consistency
2. Upload each markdown file to SageDocs via `POST /api/documents/upload`
3. Verify RAG retrieval quality with test questions from the analytics log

## Documentation Template

Each markdown file follows this structure:

```markdown
# [Module Name]

## Overview
Brief description of what this module does and when to use it.

## How to Access
Navigation path (e.g., "Click the Calendar tab in the top navigation").

## [Task 1: e.g., "Schedule a New Appointment"]
Step-by-step instructions:
1. Step one
2. Step two
3. Step three

## [Task 2: e.g., "Reschedule an Appointment"]
...

## Key Fields
| Field | Description |
|-------|-------------|
| Field Name | What it means and how to fill it |

## Tips
- Common gotchas or helpful shortcuts

## Related Topics
- Links to other relevant docs
```

## Core Modules (Phase 1 Scope)

Priority order based on user frequency and question analytics:

1. **Patient Management** - Adding, searching, editing patients
2. **Patient Chart Overview** - Summary view, demographics, insurance, cases
3. **Calendar/Scheduling** - Booking, rescheduling, calendar views, rooms
4. **Visits/EHR** - Creating visits, SOAP notes, visit types
5. **Ledger/Charges/Payments** - Posting charges, recording payments, balances
6. **Claims/Billing** - Generating claims, claim statuses, electronic vs paper
7. **Statements** - Generating patient statements
8. **Reports** - Running common reports (Daysheet, Transaction, Outstanding Claims)

## File Organization

```
backend/uploads/chirocloud/
  chirocloud-help.md          # (existing, will be replaced)
  patients.md                 # Patient management
  patient-chart.md            # Patient chart sections
  scheduling.md               # Calendar and appointments
  billing-and-finance.md      # Ledger, claims, statements, reports
```

Four files rather than 8+ individual ones. Larger documents chunk better for RAG because related content stays together, improving semantic search relevance.

## Writing Guidelines

- **Audience:** All roles — front desk, billing staff, clinic owners
- **Tone:** Clear, direct, task-oriented. No jargon without explanation.
- **Format:** Numbered steps for procedures, tables for field references
- **Terminology:** Use the exact labels from the app UI (e.g., "Visits / EHR" not "Electronic Health Records")
- **Length:** Each file 200-500 lines. Enough detail for RAG chunks but not overwhelming.
- **No screenshots in markdown:** The RAG pipeline processes text. Describe what the user sees rather than embedding images.

## Success Criteria

1. SageDocs can answer the previously unanswered questions from analytics
2. Each core module has step-by-step task documentation
3. Documentation uses exact UI labels from the live app
4. RAG retrieval returns relevant chunks for common user questions

## Risks

| Risk | Mitigation |
|------|------------|
| Captured snapshots miss interactive workflows (dropdowns, modals) | Browse interactively during capture phase, trigger key interactions |
| Documentation becomes stale as app updates | Date-stamp docs, review quarterly |
| RAG chunks split mid-procedure | Use clear headings so chunker splits at section boundaries |
| Too much detail hurts retrieval | Keep procedures concise, use "Tips" section for edge cases |
