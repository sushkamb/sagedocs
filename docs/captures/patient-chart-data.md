# Patient Chart — Captured UI Data

## How to Access
Click on any patient row in the Patient Lookup list. A new tab opens with the patient's name.

## Sidebar Navigation (Left Panel)
The patient chart has a tree-style sidebar with these sections:
1. Overview (default view)
2. Demographics
3. Employer
4. Insurance
5. Patient History
6. Cases
7. Visits / EHR
8. Ledger (expandable, with sub-items):
   - Edit Posting
   - Charges
   - Payments
   - Legacy Postings
9. Record Center

Top-right has: "Quick Selection" dropdown, "Save" button

## Overview
Displays a summary card for the patient:

**Left card — Patient Info:**
- Photo/avatar
- Account No (e.g., 18601)
- Name (e.g., Andrew Little020226 (Andy))
- DOB (e.g., 01/18/1989)
- Age (e.g., 37)
- Gender (e.g., Male)
- Phone (e.g., (916) 988-7877 (Home))
- Email (e.g., alittle@forteholdings.com)
- Address + Address 2
- Last Appointment (date)
- Next Appointment (date)
- "Contact Patient" button

**Right cards — Summary Tiles:**
- Number of Visits (e.g., 1)
- Outstanding Claims (e.g., $100.00)
- Initial Complaint (text)
- Unapplied Credit: Insurance + Patient amounts
- Insurance on File (e.g., Medicare, Kaiser of Northern California)
- Patient Balance: Insurance + Patient amounts

**Quick Action Buttons (green row):**
- Statement
- Patient Portal
- Claim
- Appointment
- Future Appointment

**Bottom sections:**
- Alerts (with edit icon, grid for alert entries)
- Notes (with edit icon, grid for note entries)

## Demographics
Same form as Add New Patient — editable fields for:
- First, MI, Last, Preferred Name
- DOB, Age, Sex
- Marital Status, Spouse/Partner
- Email, SSN
- Address, City, State, Zip
- Phone numbers (3 slots with type icons and Primary radio)
- Referral Type, Referral Source
- Email/SMS Reminder opt-in checkboxes
- User Fields 1 & 2

## Employer
- Employer details form (employer name, address, phone, etc.)

## Insurance
- Header: "Insurance List" with "+ Add New Insurance" button
- Grid columns: Insurance Company, Effective Date, End Date, Delete icon
- Example entries:
  - 3154 - Medicare, 02/02/2026 to 02/02/2027
  - 3155 - Kaiser of Northern California, 01/01/2020 to 01/01/2027
- Each row has a delete (trash) icon
- Clicking "+ Add New Insurance" opens a form to add insurance

## Patient History
- Medical history, allergies, surgeries, medications
- (Standard medical history intake form)

## Cases
- Header: "Patient Case(s)" with "+ Add New Case" button
- Grid columns: Initial Visit, Doctor, Case Type, Status, Initial Complaint, Ins. Balance, Pat. Balance
- Example entry:
  - 02/02/2026, Christopher Smith, Kaiser Permanente, Active, (blank), $100.00, $0.00
- A case groups related visits and charges for billing purposes
- Each case is tied to a doctor and case type (usually an insurance plan)

## Visits / EHR
- Header: "Visit(s)" with "+ Add New Visit" button
- Grid columns: Visit Date (sortable), Patient Case, Doctor, Visit Type, Initial Complaint, Complaints, Status, Actions
- Actions per row: Edit Visit (pencil), Copy Visit (copy icon), Delete Visit (trash)
- Example entry:
  - 02/02/2026, 02/02/2026 - Kaiser Permanente, Christopher Smith, (blank), (blank), (blank), (blue dot = active)
- Clicking Edit opens the visit/EHR editor with SOAP notes and treatment details

## Ledger > Charges
- Top: "Select Case" dropdown + "Select Visit" dropdown
- Three info cards:
  - **Case Details:** Insurance Balance, Patient Balance, Case Type, Case Insurance Details
  - **Visit Details:** Insurance Balance, Patient Balance, Patient Credits (Insurance Credit, Patient Credit)
  - **Diagnosis:** Grid with Print Order, ICDA code, Description, Diagnosis Date
- Action buttons: Add New Charge, Save Changes, Adjustments, Import EHR Treatments, Copay Estimator
- Charges grid columns: Delete icon, Status, From Date, To Date, Code, (blank), Description, Mod, Ins. Charge, Pat. Charge, Units, Diagnosis, Ins. Adjustment, Pat. Adjustment, POS, Do not bill (checkbox), Insurance, Comments, Adjudication Date
- Example charges:
  - NEW, 02/02/2026, 98941, Spinal Manipulation 3-4 Regions, $45.00 ins / $0.00 pat
  - NEW, 02/02/2026, 98942, Spinal Manipulation 5 Regions, mod AT, $55.00 ins / $0.00 pat

## Ledger > Payments
- Payment recording interface
- (Allows entering insurance payments, patient payments, apply to charges)

## Ledger > Edit Posting
- Combined view of charges and payments for editing

## Ledger > Legacy Postings
- Historical/imported postings from previous system

## Record Center
- Document management for the patient
- Upload and store PDFs, images, forms, letters
