# Billing and Finance

## Overview

TurnCloud (also known as ChiroCloud) provides a full billing and finance workflow for chiropractic practices. You can post charges and payments at the patient level, generate insurance claims and patient statements in bulk, process EOB payments, and run financial reports. Billing tasks are split between two main areas: the patient-level Ledger (inside each patient's chart) and the office-wide Financials tab (for claims, statements, and bulk payments). Reports are available under a dedicated Reports tab.

## How to Access

- **Patient-level billing (charges, payments, adjustments):** Open a patient's chart, then click "Ledger" to access Charges, Payments, and Edit Posting views.
- **Claims, Statements, and Bulk Payments:** Click the "Financials" tab in the top navigation bar. Use the left sidebar to switch between Claims, Statements, Bulk Payments, and Messages.
- **Reports (Daysheet, Transaction Report, Outstanding Claims, etc.):** Click the "Reports" tab in the top navigation bar. Use the left sidebar to select the report type.

---

## Posting Charges

Charges represent the services billed for a patient visit. Each charge line corresponds to a CPT procedure code.

### How to Add Charges to a Visit

1. Open the patient's chart.
2. Click "Ledger" to open the ledger view.
3. Click the "Charges" sub-tab.
4. Use the "Select Case" dropdown at the top to choose the correct patient case.
5. Use the "Select Visit" dropdown to choose the visit you want to bill.
6. Review the three info cards displayed: "Case Details", "Visit Details", and "Diagnosis". Confirm the diagnosis codes are correct before adding charges.
7. Click "Add New Charge" to insert a new charge line into the grid.
8. Fill in the charge fields:
   - **Status** -- The billing status of the charge (e.g., New, Billed).
   - **From Date** -- The service start date.
   - **To Date** -- The service end date (usually the same as From Date for single-day visits).
   - **Code** -- The CPT procedure code (e.g., 98941 for Spinal Manipulation 3-4 Regions).
   - **Description** -- Auto-populated from the CPT code. Can be edited if needed.
   - **Mod** -- Modifier codes (e.g., 25, 59) if applicable.
   - **Ins. Charge** -- The amount billed to insurance.
   - **Pat. Charge** -- The amount billed to the patient.
   - **Units** -- The number of units for this service (default is 1).
   - **Diagnosis** -- The diagnosis pointer(s) linking this charge to the diagnosis codes on the case.
9. Click "Save Changes" to save all charge entries.

### Importing Charges from EHR

1. On the Charges sub-tab, click "Import EHR Treatments".
2. TurnCloud pulls the treatment codes documented during the visit in the EHR module and populates them as charge lines.
3. Review the imported charges for accuracy, then click "Save Changes".

### Additional Charge Fields

The charges grid also includes these optional columns:

| Field | Description |
|---|---|
| Ins. Adjustment | Adjustment amount applied to the insurance portion |
| Pat. Adjustment | Adjustment amount applied to the patient portion |
| POS | Place of Service code (e.g., 11 for Office) |
| Do not bill | Checkbox to exclude this charge from claim generation |
| Insurance | Which insurance policy this charge is billed under |
| Comments | Free-text notes about this charge |
| Adjudication Date | Date the insurance company adjudicated this charge |

---

## Adjustments

Adjustments let you modify charge amounts after they have been posted, such as write-offs, contractual adjustments, or courtesy discounts.

1. Open the patient's chart and go to "Ledger" > "Charges".
2. Select the appropriate case and visit.
3. Click the "Adjustments" button above the charges grid.
4. Apply the adjustment amounts in the "Ins. Adjustment" or "Pat. Adjustment" columns for the relevant charge lines.
5. Click "Save Changes".

---

## Copay Estimator

The Copay Estimator helps calculate what a patient owes based on their insurance plan details.

1. Open the patient's chart and go to "Ledger" > "Charges".
2. Select the appropriate case and visit.
3. Click the "Copay Estimator" button.
4. Review the estimated patient responsibility based on the insurance configuration for this case.

---

## Recording Payments

Payments are recorded at the patient level and applied to specific charges.

### How to Record a Payment

1. Open the patient's chart.
2. Click "Ledger" to open the ledger view.
3. Click the "Payments" sub-tab.
4. Enter the payment details:
   - Select whether this is a patient payment or an insurance payment.
   - Enter the payment amount.
   - Select the payment method (cash, check, credit card, insurance EOB, etc.).
5. Apply the payment to one or more outstanding charges.
6. Save the payment.

### Edit Posting View

The "Edit Posting" sub-tab provides a combined view showing both charges and payments side by side for a patient. This is useful for reconciling what has been billed versus what has been paid on a specific case or visit.

1. Open the patient's chart and click "Ledger".
2. Click the "Edit Posting" sub-tab.
3. Review charges on one side and payments on the other.
4. Make edits as needed and save.

---

## Generating Claims

Claims are generated from the Financials tab and submitted to insurance companies either electronically or on paper.

### How to Create a New Claims Job

1. Click the "Financials" tab in the top navigation.
2. The Claims section opens by default. The left panel is "Generate New Claims Job".
3. Set your filters to select which patients and charges to include:
   - **Provider** -- Use the "Provider" dropdown to select a specific provider, or leave it set to "All Providers" to include everyone.
   - **Insurance Company** -- Type or select an insurance company to filter by payer.
   - **Case Type** -- Use the Case Type grid to "Include" or "Exclude" specific case types.
4. Optionally click "+ Add New Filter" to add more filtering criteria.
5. To save a filter combination for reuse, click "Save". To load a previously saved filter, click "Load".
6. Choose the claim format:
   - Check "Electronic" to generate X12 5010 files for electronic submission.
   - Check "Paper" to generate printable paper claims (with or without background).
7. Click "Fetch Patients" to apply filters and retrieve all patients and cases that have new or unbilled charges.
8. A patient list grid appears with columns: Account, First Name, Last Name, Patient Case, Provider, Primary Insurance, Secondary Insurance.
9. Review the patient list. You can:
   - Adjust the Account number, Case, or Provider for individual patients using the inline controls.
   - Click "Add to Billing List" to add more patients.
   - Click "Remove Selected Patients" to remove specific patients from the batch.
   - Click "Clear Billing List" to start over.
10. When the list is ready, click "Claim Settings" to review submission settings.
11. Submit the claims job. TurnCloud will process the claims and create a new entry in the Claims Jobs grid on the right panel.

### Electronic vs. Paper Claims

- **Electronic claims** produce X12 5010 (X125010) files that are transmitted to the clearinghouse for submission to insurance payers. This is the standard and fastest method.
- **Paper claims** produce PDF files formatted as CMS-1500 forms. "Paper" generates a plain form; "PaperWithBackground" includes the red CMS-1500 background template for printing on blank paper.

---

## Managing Claims Jobs

The right panel of the Claims section displays all claims jobs that have been created.

### Filtering Claims Jobs

1. In the "Filter Jobs" section at the top of the right panel, set your criteria:
   - **Start date** -- Filter jobs created on or after this date.
   - **End date** -- Filter jobs created on or before this date.
   - **Claim Status** -- Filter by status (DONE, ERROR, PROCESSING, FINAL, REPROCESS).
   - **Account** -- Search by a specific patient account number.
2. Click "Apply Filters" to update the grid.
3. Click "Refresh/Clear Filter" to reset all filters and reload.

### Claims Jobs Grid Columns

| Column | Description |
|---|---|
| Id | Unique identifier for the claims job |
| Claim Type | Format of the claim (X125010, Paper, PaperWithBackground, ItemisedStatement) |
| Date Started | When the claims job was created |
| Download Link | Link to download the generated claim file (PDF or X12) |
| Patient Count | Number of patients included in this job |
| Error Count | Number of claims that encountered errors |
| Total Claim Amount | Total dollar amount of all claims in this job |
| Parent Run ID | ID of the parent job if this is a reprocessed run |
| Status | Current status of the job |
| Actions | Buttons for viewing details, reprocessing, downloading |

### Claim Statuses

| Status | Meaning |
|---|---|
| DONE | The claims job completed successfully. All claims were generated without errors. |
| ERROR | One or more claims in the job encountered errors. Review the error count and individual claim details to identify and fix issues. |
| PROCESSING | The claims job is currently being generated. Wait for it to finish. |
| FINAL | The claims job has been finalized. No further changes can be made. |
| REPROCESS | The claims job has been marked for reprocessing, typically after fixing errors or updating charge information. |

### Downloading Claim Files

1. Find the claims job in the grid.
2. Click the link in the "Download Link" column, or click the download icon in the "Actions" column.
3. The file downloads as a PDF (for paper claims) or an X12 file (for electronic claims).

### Reprocessing a Claims Job

If a claims job has errors or if charge information was updated after submission:

1. Find the claims job in the grid.
2. Click the reprocess icon in the "Actions" column.
3. The status changes to "REPROCESS" and TurnCloud regenerates the claims.
4. A new claims job entry may be created with a "Parent Run ID" linking back to the original job.

---

## Generating Statements

Patient statements are itemized bills sent to patients for their outstanding balances.

### How to Generate Statements

1. Click the "Financials" tab in the top navigation.
2. Click "Statements" in the left sidebar.
3. Set filters to determine which patients receive statements:
   - Filter by patient name or account number.
   - Set a date range for the charges to include.
   - Set a minimum balance threshold (so you only send statements to patients who owe above a certain amount).
4. Click the "Generate" button. TurnCloud produces itemized statement PDFs.
5. The generated statement job appears in the Claims Jobs grid with a Claim Type of "ItemisedStatement".
6. Download the PDF to print and mail, or use for electronic delivery.

### Tips for Statements

- Run statements monthly or bi-weekly for patients with outstanding balances.
- Use the minimum balance filter to avoid sending statements for trivially small amounts.
- Statements list all charges, payments, and adjustments so the patient can see a full account summary.
- You can also generate a statement for a single patient directly from their chart by clicking the "Statement" quick action button on the Overview page.

---

## Bulk Payments

Bulk Payments allow you to post insurance EOB (Explanation of Benefits) payments to multiple patients and charges at once, rather than entering them one patient at a time.

### How to Post Bulk Payments

1. Click the "Financials" tab in the top navigation.
2. Click "Bulk Payments" in the left sidebar.
3. Enter the EOB details:
   - Select the insurance company.
   - Enter the check or EFT number.
   - Enter the payment date.
4. For each patient and charge on the EOB, enter:
   - The payment amount.
   - Any insurance adjustments (contractual write-offs).
   - Any denial information if applicable.
5. Apply the payments to the matching charges.
6. Save the bulk payment batch. The payments are posted to each patient's ledger.

---

## Clearinghouse Messages

The Messages section shows communications from the clearinghouse related to your submitted claims.

1. Click the "Financials" tab in the top navigation.
2. Click "Messages" in the left sidebar.
3. Review claim acknowledgments, rejections, and status updates from the clearinghouse.
4. Use these messages to identify claims that need correction and resubmission.

---

## Running Reports

TurnCloud provides several built-in reports and a custom report builder. Access all reports from the "Reports" tab in the top navigation. The left sidebar lists the available report types.

### Daysheet

The Daysheet is a daily summary report of all charges, payments, and adjustments posted on a given day. Most practices run this at the end of each business day.

1. Click the "Reports" tab in the top navigation.
2. Click "Daysheet" in the left sidebar.
3. Select the date (or date range) for the report.
4. Choose any additional filters (provider, location).
5. Click "Run" or the equivalent button to generate the report.
6. Review the summary of total charges, total payments, and total adjustments for the selected period.

### Transaction Report

The Transaction Report shows individual financial transactions (charges, payments, adjustments) for a specified date range.

1. Click the "Reports" tab.
2. Click "Transaction Report" in the left sidebar.
3. Set the date range and any filters.
4. Run the report.
5. Review line-by-line transaction details.

### Outstanding Claims

The Outstanding Claims report lists all insurance claims that have not yet been paid, typically grouped by aging buckets (30, 60, 90, 120+ days).

1. Click the "Reports" tab.
2. Click "Outstanding Claims" in the left sidebar.
3. Set filters such as date range, provider, or insurance company.
4. Run the report.
5. Review unpaid claims organized by how long they have been outstanding. Use this report to follow up with insurance companies on overdue payments.

### Billing History

The Billing History report shows a complete history of all billing activity, including claims submitted, payments received, and adjustments made.

1. Click the "Reports" tab.
2. Click "Billing History" in the left sidebar.
3. Set your date range and any additional filters.
4. Run the report to see the full billing timeline.

### EHR Reports

EHR Reports provide data related to electronic health records and visit documentation.

1. Click the "Reports" tab.
2. Click "EHR Reports" in the left sidebar.
3. Select the specific EHR report type and filters.
4. Run the report.

### Appointments Report

The Appointments report shows appointment data with various filters.

1. Click the "Reports" tab.
2. Click "Appointments" in the left sidebar.
3. Set filters such as date range, provider, appointment type, or status.
4. Run the report to review appointment data.

---

## Search Report Generator

The Search Report Generator is a powerful custom report builder that lets you query across multiple data entities and create reports tailored to your specific needs.

### How to Build a Custom Report

1. Click the "Reports" tab in the top navigation.
2. Click "Search Report Generator" in the left sidebar.
3. On the left side, you see an entity tree with checkboxes. Available entities include:
   - Patient
   - PatientAddress
   - PatientAllergy
   - PatientCase
   - PatientCaseInsurance
   - PatientEmail
   - PatientEmployer
   - PatientInsurance
   - PatientMedicalHistory
   - PatientNote
   - PatientPhone
   - PatientSurgery
   - PostingBalances
4. Check the entities you want to include in your report. For example, check "Patient" and "PostingBalances" to build a report showing patients with their account balances.
5. Configure the columns you want to display from the selected entities.
6. Set up filters to narrow the results (e.g., patients with a balance greater than $50, or patients in a specific city).
7. Use the toolbar buttons:
   - **New Filter** -- Create a new filter criterion.
   - **Open** -- Open a previously saved report template.
   - **Save** -- Save the current report configuration for future use.
   - **Run** -- Execute the report and display results.
8. Review the results in the grid below.

### Saving and Loading Custom Reports

1. After configuring your report, click "Save" in the toolbar.
2. Give the report a name.
3. To reuse it later, click "Open" and select the saved report from the list.

---

## Exporting Reports

All reports in TurnCloud can be exported for use outside the system.

### Export to Excel

1. Run any report.
2. Click the "Export to Excel" button in the results toolbar.
3. A spreadsheet file downloads to your computer with the full report data.

### Export to PDF

1. Run any report.
2. Click the "Export to PDF" button in the results toolbar.
3. A PDF file downloads with the formatted report.

### Generate Mailing Labels

This option is available in the Search Report Generator and is useful for sending physical mail to patients.

1. Run a report that includes patient address data (ensure the "PatientAddress" entity is selected).
2. Click "Generate Mailing Labels" in the results toolbar.
3. TurnCloud generates a printable label sheet formatted for standard mailing labels.

---

## Key Fields Reference

### Charge Fields

| Field | Description |
|---|---|
| Status | Billing status of the charge (New, Billed, etc.) |
| From Date | Service start date |
| To Date | Service end date |
| Code | CPT procedure code (e.g., 98941) |
| Description | Description of the procedure, auto-filled from CPT code |
| Mod | Modifier codes for the procedure |
| Ins. Charge | Amount billed to insurance |
| Pat. Charge | Amount billed to the patient |
| Units | Number of units for the service |
| Diagnosis | Diagnosis pointer linking to ICD-10 codes on the case |
| Ins. Adjustment | Insurance adjustment amount (write-off) |
| Pat. Adjustment | Patient adjustment amount |
| POS | Place of Service code |
| Do not bill | Excludes the charge from claim generation when checked |
| Insurance | Which insurance policy is billed |
| Comments | Free-text notes about the charge |
| Adjudication Date | Date insurance adjudicated the charge |

### Claims Job Fields

| Field | Description |
|---|---|
| Id | Unique job identifier |
| Claim Type | X125010 (electronic), Paper, PaperWithBackground, or ItemisedStatement |
| Date Started | When the job was created |
| Download Link | Link to download the generated file |
| Patient Count | Number of patients in the job |
| Error Count | Number of errors encountered |
| Total Claim Amount | Sum of all claim amounts in the job |
| Parent Run ID | Links to the original job if this is a reprocessed run |
| Status | DONE, ERROR, PROCESSING, FINAL, or REPROCESS |

---

## Tips

- Run the Daysheet report at the end of each business day to verify that all charges and payments were entered correctly.
- Always review the diagnosis codes on a case before posting charges. Incorrect diagnosis pointers are a common cause of claim denials.
- Use the "Fetch Patients" button in the Claims section regularly to catch any unbilled charges that may have been missed.
- Save your commonly used filter combinations in the Claims section using the "Save" button so you can quickly reload them.
- When a claims job shows errors, click into the job to review individual claim errors before reprocessing.
- Use the Outstanding Claims report weekly to follow up on unpaid claims, especially those aging past 30 days.
- The Search Report Generator is the most flexible reporting tool. If a built-in report does not meet your needs, build a custom report using the entity tree.
- Export reports to Excel when you need to do further analysis or share data with an accountant or billing service.
- When posting bulk payments from an EOB, work through each line item carefully to ensure payments and adjustments are applied to the correct charges.
- Mark charges as "Do not bill" if they should not be included in insurance claims (e.g., complimentary services).

---

## Related Topics

- **Patient Management** -- See [patients.md](patients.md) for managing patient records, demographics, and insurance information.
- **Patient Chart** -- See [patient-chart.md](patient-chart.md) for working within a patient's chart, including the Ledger, Diagnosis, and EHR tabs.
- **Calendar and Scheduling** -- See [scheduling.md](scheduling.md) for scheduling appointments and managing the calendar.
