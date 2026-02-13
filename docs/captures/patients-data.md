# Patient Management — Captured UI Data

## Patient Lookup (Home Screen under Patients Tab)
- Access: Click "Patients" tab in top navigation
- Left sidebar has: Search (text field "Search Patient", type and hit enter), Advanced Search (expandable)
- "Add New Patient" button at top
- "Load Recent Patients" dropdown (50/100/etc) with "Load Patients" button
- Patient list grid columns: Avatar initials, Account, First Name, Last Name, Birth Date, Gender, Phone
- Clicking a patient row opens their chart

## Add New Patient Form
- Access: Click "+ Add New Patient" button on Patient Lookup page
- Opens Demographics tab for the new patient
- Required fields (marked with *): First, Last
- Form fields (left column):
  - First * (text, placeholder "First Name")
  - M (text, placeholder "MI" — middle initial)
  - Preferred Name (text)
  - Marital Status (dropdown)
  - Spouse/Partner (text)
  - Photo upload area with "Active" checkbox (checked by default)
- Form fields (right column):
  - Last * (text, placeholder "Last Name")
  - Date of Birth (date picker, format month/day/year)
  - Age (auto-calculated, disabled)
  - Sex (dropdown)
  - Email (text, placeholder "name@domain.com")
  - SSN (text, placeholder "000-00-0000")
- Address section:
  - Address (text)
  - Address Line 2 (text, placeholder "Apt/Suite")
  - City (text), State (dropdown), Zip (text)
- Contact Numbers section:
  - Three phone number fields (format "(000) 000-0000")
  - Each has an icon (phone type: mobile, home, work/fax) and Primary radio button
- Other fields:
  - Referral Type (dropdown)
  - Referral Source (text)
  - Opt In to Email Reminders (checkbox, checked by default)
  - Opt In to SMS Reminders (checkbox, checked by default)
  - User Field 1 + Value (custom fields)
  - User Field 2 + Value (custom fields)
- "Save" button at top right
- Note: Visits/EHR and Ledger tabs are disabled until patient is saved

## Advanced Search
- Expandable section below Search in left sidebar
- (Not fully expanded during capture — likely has filters for name, DOB, gender, phone, etc.)

## Patient Search (Quick Access)
- Available via "Patient Search" link in sub-navigation bar below tabs
- Also via "Appointments" link in sub-navigation
