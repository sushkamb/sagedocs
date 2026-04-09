"""Mock ChiroCloud API server for testing SageDocs Data Mode.
Simulates the /api/Assistant/* endpoints that ChiroCloud would provide."""

from fastapi import FastAPI, Header
from typing import Optional
import uvicorn

app = FastAPI(title="Mock ChiroCloud API")


@app.get("/api/Assistant/GetPatientCount")
async def get_patient_count(
    date_from: str,
    date_to: str,
    status: Optional[str] = None,
    authorization: str = Header(None),
    x_account_number: str = Header(None, alias="X-Account-Number"),
):
    counts = {"new": 14, "active": 187, "inactive": 43}
    if status:
        return {"count": counts.get(status, 0)}
    return {"count": sum(counts.values())}


@app.get("/api/Assistant/GetAppointments")
async def get_appointments(
    date: Optional[str] = None,
    doctor_name: Optional[str] = None,
    authorization: str = Header(None),
    x_account_number: str = Header(None, alias="X-Account-Number"),
):
    appointments = [
        {"time": "09:00", "patient_name": "John Smith", "visit_type": "Adjustment", "status": "confirmed"},
        {"time": "09:30", "patient_name": "Mary Johnson", "visit_type": "New Patient Exam", "status": "confirmed"},
        {"time": "10:00", "patient_name": "Robert Davis", "visit_type": "Adjustment", "status": "checked_in"},
        {"time": "10:30", "patient_name": "Lisa Wilson", "visit_type": "Re-Exam", "status": "confirmed"},
        {"time": "11:00", "patient_name": "James Brown", "visit_type": "Adjustment", "status": "confirmed"},
    ]
    if doctor_name:
        # Simulate filtering
        appointments = appointments[:3]
    return {"count": len(appointments), "appointments": appointments}


@app.get("/api/Assistant/GetAgingClaims")
async def get_aging_claims(
    payer_name: Optional[str] = None,
    authorization: str = Header(None),
    x_account_number: str = Header(None, alias="X-Account-Number"),
):
    buckets = [
        {"bucket": "0-30 days", "count": 45, "total_amount": 12500.00},
        {"bucket": "31-60 days", "count": 23, "total_amount": 8750.00},
        {"bucket": "61-90 days", "count": 12, "total_amount": 5200.00},
        {"bucket": "90+ days", "count": 8, "total_amount": 3800.00},
    ]
    if payer_name:
        # Simulate filtering to fewer results
        buckets = [{"bucket": "0-30 days", "count": 5, "total_amount": 2100.00},
                   {"bucket": "31-60 days", "count": 3, "total_amount": 1400.00}]
    return buckets


@app.get("/api/Assistant/GetProviderSchedule")
async def get_provider_schedule(
    doctor_name: str,
    date: str,
    authorization: str = Header(None),
    x_account_number: str = Header(None, alias="X-Account-Number"),
):
    return [
        {"time": "09:00", "patient_name": "John Smith", "visit_type": "Adjustment", "status": "confirmed"},
        {"time": "09:30", "patient_name": "Mary Johnson", "visit_type": "New Patient Exam", "status": "confirmed"},
        {"time": "10:00", "patient_name": "Robert Davis", "visit_type": "Adjustment", "status": "checked_in"},
        {"time": "11:00", "patient_name": "James Brown", "visit_type": "Adjustment", "status": "confirmed"},
        {"time": "14:00", "patient_name": "Sarah Miller", "visit_type": "Follow-Up", "status": "confirmed"},
        {"time": "15:00", "patient_name": "Tom Anderson", "visit_type": "Adjustment", "status": "unconfirmed"},
    ]


@app.get("/api/Assistant/GetPatientBirthdays")
async def get_patient_birthdays(
    date_from: str,
    date_to: str,
    authorization: str = Header(None),
    x_account_number: str = Header(None, alias="X-Account-Number"),
):
    return [
        {"patient_name": "John Smith", "birthday": "1985-02-10", "age": 41},
        {"patient_name": "Lisa Wilson", "birthday": "1992-02-12", "age": 34},
    ]


@app.get("/api/Assistant/GetCollectionSummary")
async def get_collection_summary(
    date_from: str,
    date_to: str,
    authorization: str = Header(None),
    x_account_number: str = Header(None, alias="X-Account-Number"),
):
    return {
        "total_collected": 28450.00,
        "insurance_payments": 21200.00,
        "patient_payments": 7250.00,
        "count": 156,
    }


@app.get("/api/Assistant/GetOpenBalances")
async def get_open_balances(
    min_amount: Optional[float] = None,
    limit: Optional[int] = 20,
    authorization: str = Header(None),
    x_account_number: str = Header(None, alias="X-Account-Number"),
):
    balances = [
        {"patient_name": "Robert Davis", "balance": 1250.00, "last_visit_date": "2026-02-07"},
        {"patient_name": "James Brown", "balance": 875.00, "last_visit_date": "2026-02-05"},
        {"patient_name": "Sarah Miller", "balance": 450.00, "last_visit_date": "2026-01-28"},
        {"patient_name": "Tom Anderson", "balance": 320.00, "last_visit_date": "2026-02-03"},
    ]
    if min_amount:
        balances = [b for b in balances if b["balance"] >= min_amount]
    return balances[:limit]


@app.get("/api/Assistant/SearchPatient")
async def search_patient(
    name: str,
    authorization: str = Header(None),
    x_account_number: str = Header(None, alias="X-Account-Number"),
):
    # Simulate search
    if "smith" in name.lower():
        return [
            {"patient_name": "John Smith", "dob": "1985-02-10", "phone": "555-0101", "next_appointment": "2026-02-14 09:00", "balance": 0.00},
            {"patient_name": "Jane Smith", "dob": "1990-06-15", "phone": "555-0102", "next_appointment": None, "balance": 125.00},
        ]
    return [{"patient_name": name.title(), "dob": "1988-03-22", "phone": "555-0199", "next_appointment": "2026-02-20 10:00", "balance": 50.00}]


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8200)
