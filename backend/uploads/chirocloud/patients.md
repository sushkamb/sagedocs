# Patient Management

## Overview

Patient Management is the central hub in TurnCloud (ChiroCloud) for creating, finding, and maintaining patient demographic records. Every clinical workflow — scheduling, charting, billing — begins with a patient record. Use this module to add new patients, search for existing ones, update demographics, and quickly access recent patient records.

## How to Access

Click the "Patients" tab in the top navigation bar. This opens the Patient Lookup screen, which is the main starting point for all patient management tasks.

You can also reach patient search quickly by clicking the "Patient Search" link in the sub-navigation bar below the main tabs.

---

## Finding a Patient (Patient Lookup)

The Patient Lookup screen is the first thing you see when you click the "Patients" tab. It provides a fast way to locate any patient in the system.

### Using Quick Search

1. Click the "Patients" tab in the top navigation.
2. In the left sidebar, locate the "Search Patient" text field.
3. Type the patient's name (first or last) into the "Search Patient" field.
4. Press Enter on your keyboard to run the search.
5. Matching patients appear in the patient list grid on the right side of the screen.
6. Click on a patient row to open their chart.

The patient list grid displays the following columns:

- **Avatar initials** — The patient's initials displayed as a visual identifier.
- **Account** — The patient's unique account number in the system.
- **First Name** — The patient's first name.
- **Last Name** — The patient's last name.
- **Birth Date** — The patient's date of birth.
- **Gender** — The patient's gender.
- **Phone** — The patient's phone number on file.

### Tips for Quick Search

- You can search by first name, last name, or both.
- Partial name searches work — typing "Joh" will return results like "John," "Johnson," and "Johanna."
- If you get too many results, use the Advanced Search for more specific filtering.

---

## Advanced Search

Advanced Search gives you additional filter options to narrow down patient results when a quick name search is not specific enough.

### Using Advanced Search

1. Click the "Patients" tab in the top navigation.
2. In the left sidebar, click "Advanced Search" to expand the advanced filter options.
3. Enter your search criteria using the available filter fields (such as name, date of birth, gender, phone number, or other demographic details).
4. Click the search or apply button to run the filtered search.
5. Review the results in the patient list grid.
6. Click on a patient row to open their chart.

### When to Use Advanced Search

- When you have a common name and need to narrow results by date of birth or phone number.
- When you need to find patients matching specific demographic criteria.
- When a quick search returns too many results to sort through manually.

---

## Loading Recent Patients

The Load Recent Patients feature lets you quickly pull up a list of patients who were recently accessed or added, without typing a search query.

### How to Load Recent Patients

1. Click the "Patients" tab in the top navigation.
2. On the Patient Lookup screen, locate the "Load Recent Patients" dropdown.
3. Select how many patients to display from the dropdown (for example, 50 or 100).
4. Click the "Load Patients" button.
5. The patient list grid populates with the most recent patient records.
6. Click on any patient row to open their chart.

This is useful at the start of the day to see which patients have been recently active, or to quickly re-access a patient you were working with earlier.

---

## Adding a New Patient

Use this workflow to create a brand-new patient record in TurnCloud. You must complete the required fields before saving.

### Step-by-Step Instructions

1. Click the "Patients" tab in the top navigation.
2. Click the "+ Add New Patient" button at the top of the Patient Lookup screen.
3. The system opens a new patient form on the Demographics tab.
4. Fill in the required and optional fields as described below.
5. Click "Save" at the top right of the form.
6. Once saved, the Visits/EHR and Ledger tabs become available for the new patient.

### Required Fields

The following fields are marked with an asterisk (*) and must be completed before saving:

| Field | Description |
|-------|-------------|
| **First** * | The patient's legal first name. |
| **Last** * | The patient's legal last name. |

### Personal Information Fields

These fields appear in the top section of the Demographics form:

| Field | Description |
|-------|-------------|
| **First** * | Patient's first name. This is a required field. |
| **M** | Middle initial. Enter a single letter. |
| **Preferred Name** | The name the patient prefers to be called (e.g., a nickname). |
| **Last** * | Patient's last name. This is a required field. |
| **Date of Birth** | Patient's date of birth. Use the date picker or type in month/day/year format. |
| **Age** | Automatically calculated from the Date of Birth. This field cannot be edited manually. |
| **Marital Status** | Select from the dropdown (e.g., Single, Married, Divorced, Widowed). |
| **Sex** | Select from the dropdown to record the patient's sex. |
| **Spouse/Partner** | Enter the name of the patient's spouse or partner if applicable. |
| **Email** | Patient's email address (format: name@domain.com). Used for email reminders and communications. |
| **SSN** | Patient's Social Security Number (format: 000-00-0000). Used for insurance and billing purposes. |

### Photo and Active Status

- **Photo upload area** — You can upload a patient photo for visual identification.
- **Active checkbox** — This is checked by default when creating a new patient. Uncheck it to mark a patient as inactive (e.g., if they are no longer receiving care).

### Address Fields

| Field | Description |
|-------|-------------|
| **Address** | Street address (e.g., "123 Main Street"). |
| **Address Line 2** | Apartment, suite, or unit number (e.g., "Apt 4B"). |
| **City** | City name. |
| **State** | Select the state from the dropdown. |
| **Zip** | ZIP or postal code. |

### Contact Numbers

The form provides three phone number fields. Each phone field uses the format (000) 000-0000.

| Field | Description |
|-------|-------------|
| **Phone 1** | First phone number. Each field has an icon indicating the type (mobile, home, or work/fax). |
| **Phone 2** | Second phone number. |
| **Phone 3** | Third phone number. |
| **Primary** | Use the radio button next to each phone field to designate which number is the patient's primary contact number. |

### Referral Information

| Field | Description |
|-------|-------------|
| **Referral Type** | Select from the dropdown how the patient was referred (e.g., Doctor Referral, Walk-in, Online). |
| **Referral Source** | Enter the specific referral source (e.g., the name of the referring doctor or website). |

### Communication Preferences

| Field | Description |
|-------|-------------|
| **Opt In to Email Reminders** | Checked by default. Uncheck if the patient does not want to receive email appointment reminders. |
| **Opt In to SMS Reminders** | Checked by default. Uncheck if the patient does not want to receive text message appointment reminders. |

### Custom User Fields

| Field | Description |
|-------|-------------|
| **User Field 1** | A custom field label that your clinic can define for any additional data you need to track. |
| **Value** | The value for User Field 1. |
| **User Field 2** | A second custom field label for additional data. |
| **Value** | The value for User Field 2. |

### Important Notes About Adding Patients

- The "Visits/EHR" and "Ledger" tabs are disabled until you save the new patient record. You must click "Save" first before you can add visits, charges, or clinical notes.
- The "Active" checkbox is checked by default. Leave it checked for current patients.
- The "Age" field is automatically calculated — do not try to type in it.
- Both email and SMS reminder opt-ins are enabled by default. Always confirm the patient's preference before leaving these checked.

---

## Editing an Existing Patient

To update a patient's demographic information (name, address, phone, email, etc.), follow these steps:

### Step-by-Step Instructions

1. Click the "Patients" tab in the top navigation.
2. Search for the patient using the "Search Patient" field or Advanced Search.
3. Click on the patient's row in the patient list grid to open their chart.
4. Navigate to the "Demographics" tab within the patient's chart (this is typically the default view or the first tab).
5. Update any fields that need to be changed — for example, a new phone number, updated address, or corrected name spelling.
6. Click "Save" to apply your changes.

### Common Edits

- **Address change** — Update the Address, City, State, and Zip fields when a patient moves.
- **Phone number change** — Update the relevant phone field and adjust the Primary radio button if the patient's preferred contact number has changed.
- **Name change** — Update the First and/or Last name fields (e.g., after marriage).
- **Email update** — Change the Email field when a patient provides a new email address.
- **Marking a patient inactive** — Uncheck the "Active" checkbox if a patient is no longer being seen at the clinic. This keeps their record in the system but removes them from active patient lists.
- **Communication preferences** — Update the "Opt In to Email Reminders" or "Opt In to SMS Reminders" checkboxes based on the patient's request.

---

## Key Fields Reference

| Field | Location | Description |
|-------|----------|-------------|
| First * | Demographics — Personal Info | Patient's legal first name (required). |
| Last * | Demographics — Personal Info | Patient's legal last name (required). |
| Date of Birth | Demographics — Personal Info | Patient's birth date; used to auto-calculate Age. |
| Sex | Demographics — Personal Info | Patient's sex as selected from dropdown. |
| Email | Demographics — Personal Info | Email address for communications and reminders. |
| SSN | Demographics — Personal Info | Social Security Number for insurance and billing. |
| Address | Demographics — Address | Street address for the patient's residence. |
| Phone (Primary) | Demographics — Contact Numbers | The patient's main contact number, designated by the Primary radio button. |
| Referral Type | Demographics — Referral | How the patient was referred to the clinic. |
| Active | Demographics — Photo section | Whether the patient is currently active at the clinic. |
| Opt In to Email Reminders | Demographics — Communication | Whether the patient receives email appointment reminders. |
| Opt In to SMS Reminders | Demographics — Communication | Whether the patient receives SMS appointment reminders. |
| Account | Patient List Grid | Unique system-generated account number. |

---

## Tips

- **Always verify patient identity** before opening a chart. Confirm the patient's name, date of birth, and phone number to avoid editing the wrong record.
- **Use the Primary radio button** to mark the phone number where the patient is most easily reached. This number is typically used for appointment reminders.
- **Check communication preferences** during patient intake. Both email and SMS reminders default to opted in — confirm with the patient that they want to receive these.
- **Keep records current** by updating demographics whenever a patient reports a change of address, phone number, or insurance. Outdated information can cause claim denials and missed communications.
- **Use the Preferred Name field** for patients who go by a different name than their legal first name. This helps front desk staff address patients correctly.
- **Custom User Fields** can be configured by your clinic to track information specific to your practice needs (e.g., employer, emergency contact, or marketing source).
- **Mark patients as inactive** rather than deleting them. Inactive patients retain their full history and can be reactivated if they return to the clinic.
- **Load Recent Patients** at the start of the day to quickly see who has been recently added or accessed, saving time during busy check-in periods.

---

## Related Topics

- [Patient Chart](patient-chart.md) — Viewing and managing clinical records, visit history, and the full patient chart.
- [Scheduling](scheduling.md) — Booking, modifying, and canceling patient appointments.
- [Billing and Finance](billing-and-finance.md) — Managing charges, submitting claims, and tracking patient balances.
