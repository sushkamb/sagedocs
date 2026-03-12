import json
import os
from datetime import datetime
from fastapi import APIRouter, Depends

from app.routers.admin_auth import verify_admin_token

router = APIRouter(prefix="/api/analytics", tags=["Analytics"], dependencies=[Depends(verify_admin_token)])

ANALYTICS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "analytics")
os.makedirs(ANALYTICS_DIR, exist_ok=True)


def log_question(tenant: str, question: str, answered: bool):
    """Log a question for analytics."""
    entry = {
        "tenant": tenant,
        "question": question,
        "answered": answered,
        "timestamp": datetime.utcnow().isoformat(),
    }

    log_file = os.path.join(ANALYTICS_DIR, f"{tenant}.jsonl")
    with open(log_file, "a") as f:
        f.write(json.dumps(entry) + "\n")


@router.get("/questions")
async def get_questions(tenant: str, unanswered_only: bool = False):
    """Get logged questions for a tenant."""
    log_file = os.path.join(ANALYTICS_DIR, f"{tenant}.jsonl")

    if not os.path.exists(log_file):
        return {"tenant": tenant, "questions": []}

    questions = []
    with open(log_file, "r") as f:
        for line in f:
            entry = json.loads(line.strip())
            if unanswered_only and entry.get("answered", True):
                continue
            questions.append(entry)

    # Most recent first
    questions.reverse()
    return {"tenant": tenant, "questions": questions}


@router.get("/summary")
async def get_summary(tenant: str):
    """Get analytics summary for a tenant."""
    log_file = os.path.join(ANALYTICS_DIR, f"{tenant}.jsonl")

    if not os.path.exists(log_file):
        return {"tenant": tenant, "total": 0, "answered": 0, "unanswered": 0}

    total = 0
    answered = 0
    with open(log_file, "r") as f:
        for line in f:
            entry = json.loads(line.strip())
            total += 1
            if entry.get("answered", True):
                answered += 1

    return {
        "tenant": tenant,
        "total": total,
        "answered": answered,
        "unanswered": total - answered,
    }
