# Calendar and Scheduling

## Overview

The Calendar module in TurnCloud (ChiroCloud) is the central hub for managing patient appointments. It provides multiple calendar views, room-based scheduling, drag-and-drop rescheduling, and tools for tracking no-shows, searching appointments, and generating reports. All providers and staff can view and manage the daily schedule from this screen.

## How to Access

1. Click the "Calendar" tab in the top navigation bar.
2. The calendar opens in your default view, showing today's date.
3. You can also click the "Appointments" link in the sub-navigation bar (below the main tabs) for quick access to today's appointments.

---

## Calendar Views

TurnCloud offers four calendar views. Use the view buttons in the toolbar to switch between them.

### Day View

1. Click the "Day" button in the toolbar.
2. The calendar displays a single day with time slots in 5-minute increments from 7:00 AM to 7:55 PM.
3. Each room appears as a separate column across the top (for example, Treatment Room 1, Treatment Room 4, Massage Therapy).
4. Appointments appear as colored blocks within the time/room grid.
5. Scroll up and down to see earlier or later time slots.

### Week View

1. Click the "Week" button in the toolbar.
2. The calendar displays a full seven-day week (Sunday through Saturday).
3. Each day appears as a column.
4. Appointments are shown as blocks within each day's column.

### Work Week View

1. Click the "Work Week" button in the toolbar.
2. The calendar displays Monday through Friday only (five days).
3. This view is identical to Week view but excludes weekends, making it easier to focus on regular business days.

### Agenda View

1. Click the "Agenda" button in the toolbar.
2. The calendar switches to a list format showing appointments in chronological order.
3. This view is useful for reviewing a summary of upcoming appointments without the visual time-slot grid.

---

## Navigating the Calendar

### Jump to Today

1. Click the "Today" button in the toolbar.
2. The calendar immediately returns to the current date regardless of which date you were viewing.

### Move Forward or Backward

1. Click the right arrow ("Next") to advance by one day, one week, or one work week, depending on your current view.
2. Click the left arrow ("Previous") to go back by the same increment.
3. In Day view, the arrows move one day at a time. In Week or Work Week view, the arrows move one week at a time.

### Pick a Specific Date

1. Click the date display button in the toolbar (it shows the current date, for example "Thursday, February 12, 2026").
2. A date picker opens.
3. Select the desired date.
4. The calendar jumps to that date.

### Show Full Day

1. Click the "Show full day" button in the toolbar.
2. The calendar expands to display all hours from early morning to late evening, not just standard business hours.
3. This is useful if you need to see or schedule appointments outside of normal clinic hours.

---

## Scheduling a New Appointment

Follow these steps to book a new appointment:

1. Make sure you are in "Day" view so you can see the room columns and time slots.
2. Locate the desired time slot on the calendar by scrolling to the correct time.
3. Identify the room column where you want to book the appointment (for example, Treatment Room 1).
4. Click on the empty time slot at the intersection of the desired time and room.
5. An appointment creation dialog opens.
6. In the "Patient" field, begin typing the patient's name to search. Select the correct patient from the results.
7. Select the "Appointment Type" from the dropdown (for example, New Patient, Follow-up, Re-exam, Adjustment).
8. Select the "Provider" or doctor who will see the patient.
9. Set the "Duration" for the appointment if the default duration is not correct.
10. Review the details and click "Save" to confirm the appointment.
11. The appointment appears as a colored block on the calendar in the selected time slot and room.

If the patient does not yet exist in the system, you will need to add them as a new patient first before scheduling. See the patient registration documentation for instructions.

---

## Rescheduling an Appointment

There are two ways to reschedule an existing appointment.

### Drag and Drop

1. Locate the appointment on the calendar.
2. Click and hold the appointment block.
3. Drag it to the new desired time slot or room column.
4. Release the mouse button to drop the appointment in the new location.
5. The appointment is automatically updated with the new time and/or room.

### Edit the Appointment

1. Click on the appointment block in the calendar.
2. The appointment detail dialog opens.
3. Change the date, time, room, or provider as needed.
4. Click "Save" to confirm the changes.
5. The appointment moves to its new position on the calendar.

---

## Canceling an Appointment

1. Click on the appointment block in the calendar to open the appointment detail dialog.
2. Look for the cancel or delete option within the dialog.
3. Select the reason for cancellation if prompted.
4. Confirm the cancellation.
5. The appointment is removed from the calendar or marked as canceled, depending on your clinic's settings.

Note: Canceled appointments may still appear in appointment reports for record-keeping purposes.

---

## Managing Rooms

The left sidebar panel, labeled "Group By Rooms," controls which rooms are visible on the calendar. Each room appears as a column in Day view.

### Available Rooms

The following are examples of rooms you might see in your calendar (actual rooms depend on your clinic's configuration):

- Treatment Room 1
- Treatment Room 4
- Treatment Room 5
- Acupuncture
- Massage Therapy

### Show or Hide Rooms

1. Look at the left sidebar panel labeled "Group By Rooms."
2. Each room has a checkbox next to its name.
3. Check the box next to a room to show it as a column on the calendar.
4. Uncheck the box to hide that room from the calendar.
5. Only checked rooms appear in the Day view columns.

This is useful for focusing on specific rooms. For example, if you only work in Treatment Room 1 and Treatment Room 4, uncheck all other rooms to simplify your view.

### Configuring Rooms

Rooms are set up and managed in the administration area. To add, edit, or remove rooms:

1. Go to "Administration" in the navigation.
2. Select "Calendar Settings."
3. From here you can add new rooms, rename existing rooms, or deactivate rooms that are no longer in use.

---

## Searching Appointments

Use the search feature to find specific appointments across all dates and providers.

1. Click the "Search Appointments" button in the calendar toolbar.
2. A search dialog or panel opens.
3. Enter your search criteria. You can search by patient name, provider, appointment type, date range, or other filters as available.
4. Review the search results.
5. Click on an appointment in the results to navigate to it on the calendar or view its details.

This is especially helpful when you need to find a patient's next appointment or look up past visits without scrolling through the calendar day by day.

---

## No Show List

The No Show List helps you track patients who missed their appointments without canceling.

1. Click the "No Show List" button in the calendar toolbar.
2. A list of patients marked as no-shows is displayed.
3. Review the list to identify patients who need to be contacted for rescheduling.
4. Use this list for follow-up calls or to update patient records regarding missed appointments.

Tracking no-shows is important for maintaining accurate appointment records and for identifying patients who may need additional outreach to stay on their care plan.

---

## Exporting the Calendar to PDF

You can export the current calendar view as a PDF document for printing or sharing.

1. Click the "Export to PDF" button in the calendar toolbar.
2. The system generates a PDF of the current calendar view (Day, Week, Work Week, or Agenda, depending on which view is active).
3. Save or print the PDF as needed.

This is useful for printing out a daily schedule to post at the front desk or to share with providers who prefer a paper copy.

---

## Appointment Report

Generate reports on appointments for analysis and tracking.

1. Click the "Report" button in the calendar toolbar.
2. Set the report parameters such as date range, provider, appointment type, or status.
3. Click "Run" or "Generate" to produce the report.
4. Review the results, which may include appointment counts, no-show rates, and scheduling patterns.
5. Export or print the report as needed for your records.

Appointment reports are valuable for clinic management, helping you understand appointment volume, identify scheduling gaps, and track provider utilization.

---

## Appointment Colors and Status

Appointments on the calendar are displayed as colored blocks. The color of each block indicates the current status of the appointment:

| Color/Status | Meaning |
|--------------|---------|
| Scheduled | The appointment is booked but the patient has not yet arrived. |
| Confirmed | The patient has confirmed they will attend (via phone, email, or SMS). |
| Checked In | The patient has arrived and checked in at the front desk. |
| In Progress | The patient is currently being seen by the provider. |
| Completed | The visit is finished. |
| No Show | The patient did not arrive for their appointment. |

The exact color assigned to each status is configured under "Administration" > "Calendar Settings." Refer to your clinic's color legend to match colors to statuses. Status colors help front desk staff quickly identify which patients have arrived, which are still expected, and which appointments are complete.

---

## Key Fields

| Field | Description |
|-------|-------------|
| Patient | The patient being seen. Search by name to select. |
| Appointment Type | The reason for the visit (e.g., New Patient, Follow-up, Re-exam, Adjustment). |
| Provider | The doctor or practitioner assigned to the appointment. |
| Duration | The length of the appointment in minutes. |
| Room | The treatment room assigned to the appointment. Shown as columns in Day view. |
| Date | The date of the appointment. |
| Time | The start time of the appointment, based on the selected time slot. |
| Status | The current state of the appointment (scheduled, confirmed, checked in, etc.). Represented by color on the calendar. |

---

## Tips

- Use "Day" view for the most detailed scheduling. It shows all rooms as columns and time slots in 5-minute increments, making it easy to find openings.
- Hide unused rooms in the left sidebar to reduce clutter and make the calendar easier to read.
- Use the "Today" button to quickly return to the current date after browsing other dates.
- Drag and drop is the fastest way to reschedule. Simply grab the appointment block and move it to the new time or room.
- Check the "No Show List" regularly, ideally at the end of each day, to identify patients who need follow-up calls.
- Use "Work Week" view if your clinic does not operate on weekends. It gives a cleaner weekly overview.
- Export the daily schedule to PDF each morning and post it at the front desk for quick reference.
- Use "Search Appointments" when a patient calls and you need to quickly find their upcoming or past appointments.
- Run appointment reports weekly or monthly to track scheduling trends and identify opportunities to fill gaps.
- The "Agenda" view is ideal for a quick summary of the day's appointments without needing to interpret the time-slot grid.
- Rooms are configured under "Administration" > "Calendar Settings." Contact your system administrator if you need to add or rename rooms.

---

## Related Topics

- **Patient Management** -- See [patients.md](patients.md) for adding and managing patient records before scheduling.
- **Patient Chart** -- See [patient-chart.md](patient-chart.md) for viewing patient visit history and clinical notes linked to appointments.
- **Billing and Finance** -- See [billing-and-finance.md](billing-and-finance.md) for submitting claims and managing charges related to scheduled visits.
