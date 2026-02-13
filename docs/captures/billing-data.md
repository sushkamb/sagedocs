# Billing & Finance — Captured UI Data

## Financials Tab
Access: Click "Financials" tab in top navigation.
Left sidebar has 4 sub-sections: Claims, Statements, Bulk Payments, Messages.

---

## Claims (Default View)

### Generate New Claims Job (Left Panel)
- "+ Add New Filter" button
- "Save" / "Load" buttons for filter presets
- Provider dropdown (default: "All Providers")
- Insurance Company field
- Checkboxes: Electronic, Paper
- "Fetch Patients" button — "Apply Filters and fetch Patient/Cases with only NEW/Unbilled charges"
- Case Type grid with Include/Exclude options
- Patient list grid: Account, First Name, Last Name, Patient Case, Provider, Primary Insurance, Secondary Insurance
- Controls: Account number spinner, Case dropdown, Provider dropdown
- Buttons: "Add to Billing List", "Clear Billing List", "Remove Selected Patients"
- "Claim Settings" button

### Claims Jobs (Right Panel)
- Filter Jobs section:
  - Start date picker
  - End date picker
  - Claim Status dropdown
  - Account text field
  - "Apply Filters" / "Refresh/Clear Filter" buttons
- Claims Jobs grid columns: Expand, Id, Claim Type, Date Started, Download Link, Patient Count, Error Count, Total Claim Amount, Parent Run ID, Status, Actions
- Claim Types observed: PaperWithBackground, X125010, Paper, ItemisedStatement
- Statuses observed: DONE, ERROR, PROCESSING, FINAL, REPROCESS
- Each row has action buttons (icons for view, reprocess, download, etc.)
- Download links are generated PDFs or X12 files
- Pagination: 1-20 of 3350 items, pages 1-10+

---

## Statements
Access: Click "Statements" in left sidebar under Financials.
- Generate patient statements for outstanding balances
- Filter by patient, date range, minimum balance
- Types: Itemised statements (PDF output)

---

## Bulk Payments
Access: Click "Bulk Payments" in left sidebar under Financials.
- For posting insurance EOB (Explanation of Benefits) payments in bulk
- Apply payments to multiple patients/charges at once

---

## Messages
Access: Click "Messages" in left sidebar under Financials.
- Clearinghouse messages and responses
- Claim acknowledgments and rejections

---

## Ledger (Patient-Level, from Patient Chart)

### Charges
- Access: Patient Chart > Ledger > Charges
- Select Case dropdown + Select Visit dropdown (top)
- Three info cards: Case Details, Visit Details, Diagnosis
- Action buttons: Add New Charge, Save Changes, Adjustments, Import EHR Treatments, Copay Estimator
- Charges grid columns: Delete, Status, From Date, To Date, Code, Description, Mod, Ins. Charge, Pat. Charge, Units, Diagnosis, Ins. Adjustment, Pat. Adjustment, POS, Do not bill, Insurance, Comments, Adjudication Date
- Charge codes are CPT codes (e.g., 98941 - Spinal Manipulation 3-4 Regions)

### Payments
- Access: Patient Chart > Ledger > Payments
- Record insurance payments (from EOBs) and patient payments
- Apply payments to specific charges

### Edit Posting
- Access: Patient Chart > Ledger > Edit Posting
- Combined view showing both charges and payments side by side

---

## Reports Tab
Access: Click "Reports" tab in top navigation.
Left sidebar has 7 report types:

### Search Report Generator
- Custom report builder with entity tree (Patient, PatientAddress, PatientAllergy, PatientCase, PatientCaseInsurance, PatientEmail, PatientEmployer, PatientInsurance, PatientMedicalHistory, PatientNote, PatientPhone, PatientSurgery, PostingBalances)
- Select entities via checkboxes, configure columns and filters
- Toolbar: New Filter, Open, Save, Run buttons
- Results section: Export to Excel, Export to PDF, Generate Mailing Labels, Search filter
- Highly flexible — can create custom queries across any patient data

### Transaction Report
- Financial transaction report for a date range

### Daysheet
- Daily summary of charges, payments, and adjustments
- Standard chiropractic office report run at end of day

### Billing History
- History of all billing activity

### EHR Reports
- Reports on electronic health records / visit data

### Appointments
- Appointment reports with filters

### Outstanding Claims
- Claims that haven't been paid, grouped by aging
