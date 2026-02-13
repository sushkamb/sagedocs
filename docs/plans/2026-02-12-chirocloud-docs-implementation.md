# ChiroCloud Documentation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create 4 comprehensive markdown help documents for ChiroCloud by browsing the live app, capturing screen data, and writing documentation in parallel with an agent team.

**Architecture:** Two-phase pipeline. Phase 1 captures raw UI data from the live app into `docs/captures/` files. Phase 2 spawns 4 parallel documentation-writer agents that read captures and produce polished markdown docs in `backend/uploads/chirocloud/`. The user can then upload these files to production as needed.

**Tech Stack:** Playwright (browser automation), Markdown, ForteAI RAG pipeline

---

## Task 1: Set Up Capture Directory

**Files:**
- Create: `docs/captures/` directory

**Step 1: Create the captures directory**

```bash
mkdir -p docs/captures
```

**Step 2: Verify directory exists**

```bash
ls docs/captures/
```

Expected: Empty directory, no errors.

---

## Task 2: Capture Patient Management Screens

**Files:**
- Create: `docs/captures/patients.md`
- Create: `docs/captures/patients-home.png`
- Create: `docs/captures/patients-add-new.png`
- Create: `docs/captures/patients-advanced-search.png`

**Step 1: Navigate to Patients tab and capture**

The app is already logged in at `http://localhost/forte/ChiroCloud/Forte.ChiroCloud.WebUI/versioned/main.html`.

1. Click the "Patients" tab
2. Take a screenshot → `docs/captures/patients-home.png`
3. Save accessibility snapshot to `docs/captures/patients.md` with section header `## Patient Lookup`

**Step 2: Capture Add New Patient form**

1. Click "Add New Patient" button
2. Take a screenshot → `docs/captures/patients-add-new.png`
3. Append snapshot to `docs/captures/patients.md` under `## Add New Patient`
4. Note all form fields: First Name, Last Name, DOB, Gender, Phone, Email, Address, etc.
5. Close/cancel the form

**Step 3: Capture Advanced Search**

1. Click "Advanced Search" tree item
2. Take a screenshot → `docs/captures/patients-advanced-search.png`
3. Append snapshot to `docs/captures/patients.md` under `## Advanced Search`
4. Note all search filter fields available

**Step 4: Commit captures**

```bash
git add docs/captures/patients*
git commit -m "docs: capture patient management screens"
```

---

## Task 3: Capture Patient Chart Screens

**Files:**
- Create: `docs/captures/patient-chart.md`
- Create: `docs/captures/patient-chart-overview.png`
- Create: `docs/captures/patient-chart-demographics.png`
- Create: `docs/captures/patient-chart-insurance.png`
- Create: `docs/captures/patient-chart-cases.png`
- Create: `docs/captures/patient-chart-history.png`
- Create: `docs/captures/patient-chart-visits.png`
- Create: `docs/captures/patient-chart-record-center.png`

**Step 1: Open a patient record**

1. From Patients tab, click on a patient with data (e.g., "Andrew Little020226" account 18601)
2. The patient chart sidebar appears with: Overview, Demographics, Employer, Insurance, Patient History, Cases, Visits/EHR, Ledger, Record Center

**Step 2: Capture Overview**

1. Click "Overview" in the sidebar (should be selected by default)
2. Take screenshot → `docs/captures/patient-chart-overview.png`
3. Save snapshot to `docs/captures/patient-chart.md` under `## Overview`
4. Note: Account No, Name, DOB, Age, Gender, Phone, Email, Address, Last/Next Appointment, Number of Visits, Outstanding Claims, Initial Complaint, Unapplied Credit, Insurance on File, Patient Balance, Alerts, Notes

**Step 3: Capture Demographics**

1. Click "Demographics" in sidebar
2. Take screenshot → `docs/captures/patient-chart-demographics.png`
3. Append snapshot under `## Demographics`
4. Note all editable fields

**Step 4: Capture Insurance**

1. Click "Insurance" in sidebar
2. Take screenshot → `docs/captures/patient-chart-insurance.png`
3. Append snapshot under `## Insurance`
4. Note: insurance list, add insurance flow, fields (Company, Policy Number, Group Number, Subscriber info)

**Step 5: Capture Patient History**

1. Click "Patient History" in sidebar
2. Take screenshot → `docs/captures/patient-chart-history.png`
3. Append snapshot under `## Patient History`

**Step 6: Capture Cases**

1. Click "Cases" in sidebar
2. Take screenshot → `docs/captures/patient-chart-cases.png`
3. Append snapshot under `## Cases`
4. Note: case list, case types, create new case flow

**Step 7: Capture Visits/EHR**

1. Click "Visits / EHR" in sidebar
2. Take screenshot → `docs/captures/patient-chart-visits.png`
3. Append snapshot under `## Visits / EHR`
4. Note: visit list, create visit, SOAP notes structure, visit types

**Step 8: Capture Record Center**

1. Click "Record Center" in sidebar
2. Take screenshot → `docs/captures/patient-chart-record-center.png`
3. Append snapshot under `## Record Center`

**Step 9: Commit captures**

```bash
git add docs/captures/patient-chart*
git commit -m "docs: capture patient chart screens"
```

---

## Task 4: Capture Calendar/Scheduling Screens

**Files:**
- Create: `docs/captures/scheduling.md`
- Create: `docs/captures/calendar-day.png`
- Create: `docs/captures/calendar-week.png`
- Create: `docs/captures/calendar-agenda.png`

**Step 1: Navigate to Calendar tab**

1. Click "Calendar" tab in main navigation
2. Take screenshot of default day view → `docs/captures/calendar-day.png`
3. Save snapshot to `docs/captures/scheduling.md` under `## Day View`
4. Note: rooms listed (Treatment Room 1, Treatment Room 4, etc.), time slots, toolbar buttons (Export to PDF, Today, Previous, Next, date picker, Search Appointments, No Show List, Report)

**Step 2: Capture Week view**

1. Click "Week" button in calendar toolbar
2. Take screenshot → `docs/captures/calendar-week.png`
3. Append snapshot under `## Week View`

**Step 3: Capture Agenda view**

1. Click "Agenda" button
2. Take screenshot → `docs/captures/calendar-agenda.png`
3. Append snapshot under `## Agenda View`

**Step 4: Capture booking an appointment**

1. Click on an empty time slot in Day view
2. Note the appointment creation dialog fields
3. Append snapshot under `## Book an Appointment`
4. Cancel/close the dialog

**Step 5: Capture room list**

1. Note the room sidebar (checkboxes for rooms: Treatment Room 1, Treatment Room 4, Treatment Room 5, Accupuncture, Massage Therapy, etc.)
2. Append to `docs/captures/scheduling.md` under `## Room Management`

**Step 6: Commit captures**

```bash
git add docs/captures/scheduling* docs/captures/calendar*
git commit -m "docs: capture calendar and scheduling screens"
```

---

## Task 5: Capture Billing & Finance Screens

**Files:**
- Create: `docs/captures/billing.md`
- Create: `docs/captures/ledger.png`
- Create: `docs/captures/ledger-charges.png`
- Create: `docs/captures/ledger-payments.png`
- Create: `docs/captures/claims.png`
- Create: `docs/captures/statements.png`
- Create: `docs/captures/reports-daysheet.png`
- Create: `docs/captures/reports-transaction.png`
- Create: `docs/captures/reports-outstanding.png`

**Step 1: Capture Ledger (from patient chart)**

1. Open a patient record (e.g., Andrew Little)
2. Click "Ledger" in sidebar, then each sub-item:
   - "Edit Posting" → screenshot + snapshot
   - "Charges" → screenshot + snapshot
   - "Payments" → screenshot + snapshot
3. Save all to `docs/captures/billing.md` under `## Ledger`, `## Charges`, `## Payments`

**Step 2: Capture Claims (Financials tab)**

1. Click "Financials" tab in main navigation
2. Default view is Claims → Take screenshot `docs/captures/claims.png`
3. Append snapshot under `## Claims`
4. Note: Generate New Claims Job section, provider filter, insurance company, Electronic/Paper toggle, Fetch Patients button, Claims Jobs list with statuses (DONE, ERROR, PROCESSING, FINAL, REPROCESS)

**Step 3: Capture Statements**

1. Click "Statements" in left sidebar of Financials
2. Take screenshot → `docs/captures/statements.png`
3. Append snapshot under `## Statements`

**Step 4: Capture Bulk Payments**

1. Click "Bulk Payments" in left sidebar
2. Append snapshot under `## Bulk Payments`

**Step 5: Capture Reports**

1. Click "Reports" tab
2. For each report type, click it and capture:
   - "Daysheet" → screenshot + snapshot
   - "Transaction Report" → screenshot + snapshot
   - "Outstanding Claims" → screenshot + snapshot
3. Save under `## Daysheet Report`, `## Transaction Report`, `## Outstanding Claims Report`

**Step 6: Commit captures**

```bash
git add docs/captures/billing* docs/captures/ledger* docs/captures/claims* docs/captures/statements* docs/captures/reports*
git commit -m "docs: capture billing, finance, and reports screens"
```

---

## Task 6: Write Documentation with Agent Team

**Files:**
- Create: `backend/uploads/chirocloud/patients.md`
- Create: `backend/uploads/chirocloud/patient-chart.md`
- Create: `backend/uploads/chirocloud/scheduling.md`
- Create: `backend/uploads/chirocloud/billing-and-finance.md`

**Step 1: Spawn 4 parallel documentation-writer agents**

Each agent is a `general-purpose` subagent with a specific prompt. All agents share these instructions:

**Shared writing guidelines (include in each agent prompt):**
```
DOCUMENTATION TEMPLATE — follow this structure exactly:

# [Module Name]

## Overview
Brief description (2-3 sentences) of what this module does and when to use it.

## How to Access
Navigation path (e.g., "Click the Calendar tab in the top navigation").

## [Task Name, e.g., "Schedule a New Appointment"]
Step-by-step instructions:
1. Step with exact UI label in quotes (e.g., Click "Add New Patient")
2. Next step
3. Next step

## Key Fields
| Field | Description |
|-------|-------------|
| Field Name | What it means and expected format |

## Tips
- Practical advice, common gotchas, shortcuts

## Related Topics
- Cross-references to other doc files

WRITING RULES:
- Audience: Front desk staff, billing staff, clinic owners
- Tone: Clear, direct, task-oriented
- Use exact UI labels from the captured snapshots (e.g., "Visits / EHR" not "EHR")
- Target length: 200-400 lines per file
- No screenshots or images — text only for RAG ingestion
- Use ## headings for each major task so the RAG chunker splits cleanly
- Each procedure should be self-contained (reader shouldn't need to read another section first)
```

**Agent 1 prompt:**
```
Read the captured data at docs/captures/patients.md and all patients-*.png screenshots.
Write comprehensive documentation for Patient Management.
Cover: Patient Lookup, searching patients, Add New Patient (all fields), Advanced Search, editing patient info.
Save to: backend/uploads/chirocloud/patients.md
```

**Agent 2 prompt:**
```
Read the captured data at docs/captures/patient-chart.md and all patient-chart-*.png screenshots.
Write comprehensive documentation for the Patient Chart.
Cover: Overview (what each metric means), Demographics, Insurance (add/edit), Patient History, Cases (create/manage), Visits/EHR (create visit, SOAP notes), Record Center.
Also cover the quick action buttons: Statement, Patient Portal, Claim, Appointment, Future Appointment, Contact Patient.
Save to: backend/uploads/chirocloud/patient-chart.md
```

**Agent 3 prompt:**
```
Read the captured data at docs/captures/scheduling.md and all calendar-*.png screenshots.
Write comprehensive documentation for Calendar and Scheduling.
Cover: Day/Week/Work Week/Agenda views, booking appointments (click time slot), rescheduling, room management (sidebar checkboxes), Search Appointments, No Show List, Export to PDF.
Save to: backend/uploads/chirocloud/scheduling.md
```

**Agent 4 prompt:**
```
Read the captured data at docs/captures/billing.md and related screenshots.
Write comprehensive documentation for Billing and Finance.
Cover: Ledger overview (Edit Posting, Charges, Payments), Claims (generating new claims, claim types: X12/Paper, claim statuses: DONE/ERROR/PROCESSING/FINAL/REPROCESS, filtering), Statements (generating patient statements), Bulk Payments, common Reports (Daysheet, Transaction Report, Outstanding Claims — how to run each, filters, export to Excel/PDF).
Save to: backend/uploads/chirocloud/billing-and-finance.md
```

**Step 2: Run all 4 agents in parallel**

Use the Task tool with `subagent_type: "general-purpose"` for each agent. All 4 should be launched in a single message for parallel execution.

**Step 3: Verify output files exist**

```bash
ls -la backend/uploads/chirocloud/*.md
```

Expected: 5 files (4 new + 1 existing `chirocloud-help.md`)

**Step 4: Commit documentation**

```bash
git add backend/uploads/chirocloud/patients.md backend/uploads/chirocloud/patient-chart.md backend/uploads/chirocloud/scheduling.md backend/uploads/chirocloud/billing-and-finance.md
git commit -m "docs: add ChiroCloud help documentation for core modules"
```

---

## Task 7: Review Documentation Quality

**Step 1: Read each generated doc and verify**

For each of the 4 files:
1. Read the file
2. Check that it follows the template (Overview, How to Access, Tasks, Key Fields, Tips)
3. Verify UI labels match what was captured (exact button names, tab names)
4. Check length is 200-400 lines
5. Ensure procedures are self-contained

**Step 2: Fix any issues**

If any doc is too short, missing sections, or uses wrong UI labels — edit it directly.

**Step 3: Commit fixes**

```bash
git add backend/uploads/chirocloud/*.md
git commit -m "docs: review and polish ChiroCloud documentation"
```

---

## Task 8: Upload to Local ForteAI and Verify

**Prerequisite:** ForteAI backend must be running at `localhost:8500`.

**Step 1: Check if ForteAI is running**

```bash
curl -s http://localhost:8500/api/tenants/chirocloud | head -5
```

If not running, start it:
```bash
cd backend && source venv/bin/activate && uvicorn app.main:app --reload --port 8500 &
```

**Step 2: Upload each doc**

```bash
# Upload patients.md
curl -X POST http://localhost:8500/api/documents/upload \
  -F "file=@backend/uploads/chirocloud/patients.md" \
  -F "tenant=chirocloud" \
  -F "title=Patient Management Guide"

# Upload patient-chart.md
curl -X POST http://localhost:8500/api/documents/upload \
  -F "file=@backend/uploads/chirocloud/patient-chart.md" \
  -F "tenant=chirocloud" \
  -F "title=Patient Chart Guide"

# Upload scheduling.md
curl -X POST http://localhost:8500/api/documents/upload \
  -F "file=@backend/uploads/chirocloud/scheduling.md" \
  -F "tenant=chirocloud" \
  -F "title=Calendar and Scheduling Guide"

# Upload billing-and-finance.md
curl -X POST http://localhost:8500/api/documents/upload \
  -F "file=@backend/uploads/chirocloud/billing-and-finance.md" \
  -F "tenant=chirocloud" \
  -F "title=Billing and Finance Guide"
```

**Step 3: Verify uploads**

```bash
curl -s http://localhost:8500/api/documents/list?tenant=chirocloud
```

Expected: All 4 new documents listed alongside the existing `chirocloud-help.md`.

**Step 4: Test RAG with sample questions**

```bash
# Test patient question
curl -s -X POST http://localhost:8500/api/chat/help \
  -H "Content-Type: application/json" \
  -d '{"tenant":"chirocloud","message":"How do I add a new patient?"}' | python3 -m json.tool

# Test scheduling question
curl -s -X POST http://localhost:8500/api/chat/help \
  -H "Content-Type: application/json" \
  -d '{"tenant":"chirocloud","message":"How do I schedule an appointment?"}' | python3 -m json.tool

# Test billing question
curl -s -X POST http://localhost:8500/api/chat/help \
  -H "Content-Type: application/json" \
  -d '{"tenant":"chirocloud","message":"How do I submit a claim?"}' | python3 -m json.tool

# Test patient chart question
curl -s -X POST http://localhost:8500/api/chat/help \
  -H "Content-Type: application/json" \
  -d '{"tenant":"chirocloud","message":"How do I add insurance for a patient?"}' | python3 -m json.tool
```

Expected: Each returns a relevant, detailed answer citing the new documentation.

---

## Summary

| Task | Description | Type |
|------|-------------|------|
| 1 | Create capture directory | Setup |
| 2 | Capture patient management screens | Browser capture |
| 3 | Capture patient chart screens | Browser capture |
| 4 | Capture calendar/scheduling screens | Browser capture |
| 5 | Capture billing & finance screens | Browser capture |
| 6 | Write docs with 4 parallel agents | Agent team |
| 7 | Review documentation quality | Manual review |
| 8 | Upload to ForteAI and verify RAG | Integration test |

**Output files available for production upload:**
```
backend/uploads/chirocloud/
  patients.md              # Patient management
  patient-chart.md         # Patient chart sections
  scheduling.md            # Calendar and appointments
  billing-and-finance.md   # Ledger, claims, statements, reports
```

These files are standalone markdown — copy them to any ForteAI production instance and upload via the admin dashboard or API.
