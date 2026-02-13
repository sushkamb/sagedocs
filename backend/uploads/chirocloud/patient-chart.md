# Patient Chart

## Overview

The Patient Chart is the central hub for all information related to a single patient in TurnCloud (ChiroCloud). It consolidates demographics, insurance, medical history, cases, visits, billing, and documents into one tabbed interface. Each patient chart opens in its own tab, so you can work with multiple patients at the same time.

The chart is divided into a left sidebar for navigation and a main content area that changes based on the selected section. The sidebar sections are: Overview, Demographics, Employer, Insurance, Patient History, Cases, Visits / EHR, Ledger (with sub-sections), and Record Center.

## How to Access

1. Click the "Patients" tab in the top navigation bar.
2. Use the Patient Lookup list to find the patient by name, account number, or other search criteria.
3. Click on the patient's row in the search results.
4. A new tab opens with the patient's name, displaying the Patient Chart.

You can also access a patient chart by clicking a patient name from the Schedule view or from a billing report.

## Patient Overview

The Overview is the default view when you open a patient chart. It provides a snapshot of the patient's key information and quick access to common actions.

### Patient Info Card

The left side of the Overview displays the patient's primary details:

- **Photo/Avatar** -- The patient's photo, if one has been uploaded.
- **Account No** -- The unique account number assigned to the patient (e.g., 18601).
- **Name** -- Full name with preferred name in parentheses (e.g., Andrew Little (Andy)).
- **DOB** -- Date of birth.
- **Age** -- Calculated automatically from the date of birth.
- **Gender** -- The patient's gender.
- **Phone** -- Primary phone number with type label (e.g., Home, Cell).
- **Email** -- Email address on file.
- **Address** -- Street address, including Address 2 if applicable.
- **Last Appointment** -- The date of the patient's most recent appointment.
- **Next Appointment** -- The date of the patient's next scheduled appointment.

### Summary Tiles

The right side of the Overview shows summary tiles that give you a quick financial and clinical snapshot:

| Tile | Description |
|------|-------------|
| Number of Visits | Total count of visits recorded for this patient across all cases. |
| Outstanding Claims | Total dollar amount of claims that have been submitted but not yet paid by insurance. |
| Initial Complaint | The patient's primary complaint or reason for seeking treatment. |
| Unapplied Credit | Credit amounts that have been received but not yet applied to specific charges. Shown separately for Insurance and Patient amounts. |
| Insurance on File | Lists the names of all active insurance policies on the patient's record (e.g., Medicare, Kaiser of Northern California). |
| Patient Balance | The total amount owed, broken out by Insurance Balance and Patient Balance. |

### Understanding the Summary Tiles

- **Number of Visits** helps you see the patient's treatment history at a glance.
- **Outstanding Claims** tells you how much money is still expected from insurance companies.
- **Unapplied Credit** indicates payments received that need to be posted to specific charges. If this amount is not zero, someone should apply the credit through the Ledger.
- **Patient Balance** shows what the patient personally owes (Patient amount) versus what insurance still owes (Insurance amount). Use this to know whether to collect from the patient at their next visit.

---

## Quick Action Buttons

A row of green action buttons appears on the Overview page for fast access to common tasks:

### Statement
1. Click "Statement" on the Overview page.
2. TurnCloud generates a statement for the patient showing charges, payments, and balances.
3. Print or save the statement as needed.

Use statements when a patient requests an itemized summary of their account or when sending balance reminders.

### Patient Portal
1. Click "Patient Portal" on the Overview page.
2. This opens or manages the patient's portal access, where patients can view their own information, fill out intake forms, and communicate with the clinic.

### Claim
1. Click "Claim" on the Overview page.
2. Select the visit and insurance to create a claim.
3. Review the claim details, diagnosis codes, and procedure codes.
4. Submit the claim electronically.

### Appointment
1. Click "Appointment" on the Overview page.
2. The scheduling interface opens with the patient pre-selected.
3. Choose the date, time, provider, and appointment type.
4. Click "Save" to book the appointment.

### Future Appointment
1. Click "Future Appointment" on the Overview page.
2. Schedule an appointment for a future date without specifying an exact time slot.
3. This is useful for booking follow-up visits that are weeks or months out.

### Contact Patient
1. Click the "Contact Patient" button on the patient info card.
2. Choose the method of contact (phone, email, or SMS depending on your clinic's configuration).
3. Send a message or log the contact attempt.

---

## Alerts and Notes

Below the summary tiles on the Overview page, there are two sections for tracking important information:

### Alerts

Alerts are high-priority notices about a patient that should be seen by anyone opening the chart. Examples include allergy warnings, payment issues, or special instructions.

1. Click the edit icon (pencil) next to the "Alerts" heading.
2. Enter the alert text.
3. Click "Save."

Alerts are displayed prominently so that front desk staff, billing staff, and providers are all aware of critical information.

### Notes

Notes are general-purpose comments about the patient. They are less urgent than alerts and are used for internal communication.

1. Click the edit icon (pencil) next to the "Notes" heading.
2. Enter the note text.
3. Click "Save."

Use notes for things like patient preferences, special scheduling requests, or follow-up reminders.

---

## Demographics

The Demographics section contains all of the patient's personal and contact information. This is the same form used when adding a new patient, but here it is editable for updates.

### Editing Patient Demographics

1. Click "Demographics" in the left sidebar of the patient chart.
2. Update any of the following fields as needed:

| Field | Description |
|-------|-------------|
| First Name | Patient's legal first name. |
| MI | Middle initial. |
| Last Name | Patient's legal last name. |
| Preferred Name | The name the patient prefers to be called (nickname). |
| DOB | Date of birth. |
| Age | Automatically calculated from DOB. |
| Sex | Patient's sex. |
| Marital Status | Single, Married, Divorced, Widowed, etc. |
| Spouse/Partner | Name of spouse or partner. |
| Email | Email address for correspondence and portal access. |
| SSN | Social Security Number (used for insurance claims). |
| Address | Street address line 1. |
| City | City. |
| State | State. |
| Zip | ZIP code. |
| Phone (3 slots) | Up to three phone numbers, each with a type (Home, Cell, Work). Select which is "Primary" using the radio button. |
| Referral Type | How the patient was referred (e.g., Doctor, Internet, Friend). |
| Referral Source | The specific referral source name. |
| Email Reminders | Check this box to opt the patient in to email appointment reminders. |
| SMS Reminders | Check this box to opt the patient in to SMS text appointment reminders. |
| User Field 1 | Custom field for your clinic's use. |
| User Field 2 | Custom field for your clinic's use. |

3. Click "Save" in the top-right corner of the page to save your changes.

### Tips for Demographics

- Always verify phone numbers and email at each visit so reminders reach the patient.
- The "Primary" radio button next to phone numbers determines which number is used for automated reminders and outreach.
- Referral Type and Referral Source help your clinic track marketing effectiveness.

---

## Employer

The Employer section stores the patient's employment information. This can be important for workers' compensation cases or when employer-sponsored insurance requires employer details on claims.

1. Click "Employer" in the left sidebar.
2. Fill in or update the employer name, address, and phone number.
3. Click "Save."

---

## Insurance

The Insurance section lists all insurance policies on file for the patient and allows you to add, view, or remove policies.

### Viewing Insurance Policies

1. Click "Insurance" in the left sidebar.
2. The "Insurance List" grid shows all policies with columns for Insurance Company, Effective Date, End Date, and a delete icon.

### Adding a New Insurance Policy

1. Click "Insurance" in the left sidebar.
2. Click the "+ Add New Insurance" button at the top of the Insurance List.
3. Fill in the required fields:
   - Insurance company name (search or select from the list).
   - Policy number.
   - Group number.
   - Effective date and end date.
   - Subscriber information (if the subscriber is someone other than the patient).
4. Click "Save."

### Deleting an Insurance Policy

1. Click "Insurance" in the left sidebar.
2. Find the policy you want to remove in the Insurance List grid.
3. Click the trash icon at the end of that row.
4. Confirm the deletion when prompted.

**Important:** Deleting an insurance policy does not affect claims that have already been submitted under that policy. However, you will not be able to create new claims against a deleted policy. If a policy has ended, consider updating the end date instead of deleting it so that you retain the historical record.

### Insurance Key Fields

| Field | Description |
|-------|-------------|
| Insurance Company | The name and ID of the insurance carrier (e.g., 3154 - Medicare). |
| Effective Date | The date the policy coverage begins. |
| End Date | The date the policy coverage ends. |

---

## Patient History

The Patient History section stores the patient's medical history, including allergies, past surgeries, medications, and other health conditions. This information is typically collected during the patient's initial intake.

### Updating Patient History

1. Click "Patient History" in the left sidebar.
2. Review and update the medical history intake form. Common sections include:
   - Past medical conditions
   - Allergies
   - Current medications
   - Past surgeries or hospitalizations
   - Family medical history
3. Click "Save" to store changes.

Accurate patient history is critical for providers making treatment decisions and for insurance documentation.

---

## Cases

A case in TurnCloud groups related visits, charges, and billing for a specific course of treatment. For example, a patient who comes in for low back pain may have one case tied to their Kaiser insurance, and later a separate case for a motor vehicle accident tied to auto insurance.

### Viewing Cases

1. Click "Cases" in the left sidebar.
2. The "Patient Case(s)" grid displays all cases with the following columns:

| Column | Description |
|--------|-------------|
| Initial Visit | The date of the first visit associated with this case. |
| Doctor | The treating provider assigned to the case. |
| Case Type | Usually corresponds to the insurance plan or payer (e.g., Kaiser Permanente, Workers Comp, Cash). |
| Status | Active or Inactive. Active cases can have new visits and charges added. |
| Initial Complaint | The patient's primary complaint for this case. |
| Ins. Balance | The total amount owed by insurance for all charges in this case. |
| Pat. Balance | The total amount owed by the patient for all charges in this case. |

### Creating a New Case

1. Click "Cases" in the left sidebar.
2. Click the "+ Add New Case" button.
3. Fill in the case details:
   - Select the treating doctor.
   - Choose the case type (typically matches the insurance plan).
   - Set the status to "Active."
   - Enter the initial complaint if known.
4. Click "Save."

### When to Create a New Case

- When a patient starts treatment for a new condition.
- When a patient switches insurance plans and the new plan should be billed separately.
- When a patient has a personal injury, auto accident, or workers' compensation claim that must be tracked independently.
- When a patient returns after a gap in treatment and needs a new authorization.

### Tips for Cases

- Every visit must be linked to a case. You cannot add a visit without first having an active case.
- Keep cases organized by closing (setting to "Inactive") cases that are no longer in active treatment.
- The Ins. Balance and Pat. Balance columns give you a quick look at outstanding amounts per case without opening the Ledger.

---

## Visits / EHR

The Visits / EHR section lists all clinical visits for the patient and provides access to the electronic health record (EHR) editor where providers document SOAP notes and treatment details.

### Viewing Visits

1. Click "Visits / EHR" in the left sidebar.
2. The "Visit(s)" grid displays all visits with the following columns:

| Column | Description |
|--------|-------------|
| Visit Date | The date of the visit. Click the column header to sort. |
| Patient Case | The case this visit is linked to (shows date and case type). |
| Doctor | The provider who performed the visit. |
| Visit Type | The type of visit (e.g., New Patient, Follow-Up, Re-Exam). |
| Initial Complaint | The patient's primary complaint at this visit. |
| Complaints | Additional complaints documented. |
| Status | The visit status, shown as a colored dot (e.g., blue dot for active). |
| Actions | Icons for Edit, Copy, and Delete. |

### Adding a New Visit

1. Click "Visits / EHR" in the left sidebar.
2. Click the "+ Add New Visit" button.
3. Select the patient case to link this visit to.
4. Choose the visit date, doctor, and visit type.
5. Click "Save" to create the visit.
6. The visit appears in the grid. Click the edit (pencil) icon to open the EHR editor and document the visit.

### Editing a Visit

1. Click "Visits / EHR" in the left sidebar.
2. Find the visit in the grid.
3. Click the pencil icon in the "Actions" column.
4. The EHR editor opens, where you can enter or update SOAP notes, treatment details, diagnoses, and procedure codes.
5. Save your changes within the EHR editor.

### Copying a Visit

1. Click "Visits / EHR" in the left sidebar.
2. Find the visit you want to copy in the grid.
3. Click the copy icon in the "Actions" column.
4. A new visit is created with the same clinical data. Update the visit date and any details that differ.
5. Click "Save."

Copying is useful for follow-up visits where the treatment plan is similar to a previous visit.

### Deleting a Visit

1. Click "Visits / EHR" in the left sidebar.
2. Find the visit you want to delete.
3. Click the trash icon in the "Actions" column.
4. Confirm the deletion when prompted.

**Important:** Deleting a visit also removes any associated clinical documentation. If charges have already been posted for this visit, review the Ledger before deleting. Consider whether setting the visit to an inactive status is more appropriate than deleting it.

---

## Ledger

The Ledger section manages the financial side of the patient's care. It is organized into sub-sections accessible from the left sidebar under the "Ledger" heading.

### Charges

The Charges sub-section is where procedure codes and fees are posted for each visit.

1. Click "Ledger" in the left sidebar to expand it, then click "Charges."
2. Use the "Select Case" dropdown to choose the patient case.
3. Use the "Select Visit" dropdown to choose the specific visit.
4. Three information cards appear at the top:
   - **Case Details** -- Shows Insurance Balance, Patient Balance, Case Type, and Case Insurance Details.
   - **Visit Details** -- Shows Insurance Balance, Patient Balance, and Patient Credits (Insurance Credit, Patient Credit).
   - **Diagnosis** -- A grid showing Print Order, ICD-A code, Description, and Diagnosis Date.
5. To add a charge, click "Add New Charge."
6. Enter the procedure code (CPT), description, modifier (if any), insurance charge amount, patient charge amount, units, diagnosis pointer, and place of service (POS).
7. Click "Save Changes."

#### Charges Grid Columns

| Column | Description |
|--------|-------------|
| Status | Charge status (e.g., NEW, SUBMITTED, PAID). |
| From Date / To Date | The date range for the service. |
| Code | The CPT or procedure code. |
| Description | Description of the procedure. |
| Mod | Modifier code (e.g., AT for active treatment). |
| Ins. Charge | The amount billed to insurance. |
| Pat. Charge | The amount billed to the patient. |
| Units | Number of units for the procedure. |
| Diagnosis | Diagnosis pointer linking to the ICD code. |
| Ins. Adjustment | Insurance adjustment amount. |
| Pat. Adjustment | Patient adjustment amount. |
| POS | Place of service code. |
| Do not bill | Checkbox to exclude this charge from claims. |
| Insurance | The insurance payer for this charge. |
| Comments | Free-text comments about the charge. |
| Adjudication Date | The date the insurance company processed the claim. |

#### Additional Charge Actions

- **Adjustments** -- Apply write-offs or adjustments to charges.
- **Import EHR Treatments** -- Pull in procedure codes directly from the EHR visit documentation, saving time on manual entry.
- **Copay Estimator** -- Estimate the patient's copay based on their insurance plan.

### Payments

1. Click "Ledger" then "Payments" in the left sidebar.
2. Record insurance payments or patient payments.
3. Apply payments to specific charges.

### Edit Posting

1. Click "Ledger" then "Edit Posting" in the left sidebar.
2. This provides a combined view of charges and payments for a visit, allowing you to edit both in one place.

### Legacy Postings

1. Click "Ledger" then "Legacy Postings" in the left sidebar.
2. This section contains historical postings imported from a previous system. These records are read-only and kept for reference.

---

## Record Center

The Record Center is the patient's document repository. Use it to upload, store, and manage files such as intake forms, referral letters, imaging reports, insurance cards, and any other documents related to the patient.

### Uploading a Document

1. Click "Record Center" in the left sidebar.
2. Click the upload button or drag and drop files into the upload area.
3. Select the file from your computer (PDF, image, or other supported format).
4. Add a description or category tag if prompted.
5. Click "Save" or "Upload."

### Viewing Documents

1. Click "Record Center" in the left sidebar.
2. Browse the list of uploaded documents.
3. Click on a document to open or download it.

### Tips for Record Center

- Keep document names descriptive (e.g., "MRI Report - Lumbar 2026-01-15") so they are easy to find later.
- Upload insurance cards and ID documents so front desk staff can reference them without asking the patient again.

---

## Saving Changes

The "Save" button appears in the top-right corner of the patient chart. After making changes in any section (Demographics, Employer, Insurance, Patient History, etc.), always click "Save" to commit your changes. If you navigate away from a section without saving, your changes may be lost.

## Quick Selection

The "Quick Selection" dropdown in the top-right corner allows you to jump to a specific section of the patient chart without scrolling through the sidebar. This is especially helpful in busy workflows when you need to quickly switch between sections.

## Key Fields Reference

| Field | Location | Description |
|-------|----------|-------------|
| Account No | Overview | Unique patient identifier in TurnCloud. |
| Number of Visits | Overview tile | Total visits across all cases. |
| Outstanding Claims | Overview tile | Dollar amount of unpaid insurance claims. |
| Initial Complaint | Overview tile / Cases | The patient's primary reason for treatment. |
| Unapplied Credit | Overview tile | Payments received but not yet applied to charges. |
| Insurance on File | Overview tile | Active insurance policies. |
| Patient Balance | Overview tile | Total amount owed (Insurance + Patient). |
| Case Type | Cases | The insurance plan or payer type for a case. |
| Status (Case) | Cases | Active or Inactive. |
| Ins. Balance | Cases | Insurance balance for a specific case. |
| Pat. Balance | Cases | Patient balance for a specific case. |
| Visit Date | Visits / EHR | Date the visit occurred. |
| Visit Type | Visits / EHR | Category of visit (New Patient, Follow-Up, etc.). |
| CPT Code | Ledger > Charges | Procedure code for a billed service. |
| POS | Ledger > Charges | Place of service code. |

## Tips

- **Use the Overview first.** Before diving into details, check the Overview tiles for a quick snapshot of the patient's status, balances, and upcoming appointments.
- **Keep insurance current.** Update effective dates and end dates as policies change. This prevents claim rejections.
- **One case per course of treatment.** Do not mix unrelated conditions or different insurance plans in the same case.
- **Close inactive cases.** Setting old cases to "Inactive" keeps the Cases list clean and prevents accidental billing to the wrong case.
- **Copy visits for recurring treatments.** Use the copy icon to duplicate a visit when the patient receives the same treatment each time, then adjust as needed.
- **Check Unapplied Credit regularly.** If the Unapplied Credit tile shows a balance, apply those credits through the Ledger to keep the account accurate.
- **Save often.** Click "Save" after every change. TurnCloud does not auto-save in most sections.
- **Use Alerts for critical info.** If a patient has a drug allergy or a collections hold, put it in Alerts so every staff member sees it when opening the chart.

## Related Topics

- **Patient Lookup and Adding New Patients** -- See [patients.md](patients.md) for instructions on searching for patients, adding new patient records, and managing the patient list.
- **Scheduling** -- See [scheduling.md](scheduling.md) for booking, rescheduling, and canceling appointments from the Schedule view.
- **Billing and Finance** -- See [billing-and-finance.md](billing-and-finance.md) for a deeper look at claims, payment posting, adjustments, and financial reports.
