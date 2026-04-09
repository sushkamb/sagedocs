"""End-to-end test for SageDocs Data Mode (Phase 2).

Requires:
  1. Mock ChiroCloud running on port 8200:  python tests/mock_chirocloud.py
  2. SageDocs backend running on port 8500:  uvicorn app.main:app --port 8500

Runs a battery of natural-language questions through /api/chat/data and
validates the full pipeline: LLM tool selection → API call → response formatting.
"""

import httpx
import asyncio
import json
import sys

API_BASE = "http://localhost:8500"

# Test cases: (question, expected_tool, description)
TEST_CASES = [
    (
        "How many new patients this month?",
        "get_patient_count",
        "Should call get_patient_count with status=new and current month range",
    ),
    (
        "How many patients are scheduled today?",
        "get_appointments_today",
        "Should call get_appointments_today",
    ),
    (
        "What claims are past 90 days?",
        "get_aging_claims",
        "Should call get_aging_claims",
    ),
    (
        "What's Dr. Smith's schedule for Friday?",
        "get_provider_schedule",
        "Should call get_provider_schedule with doctor_name",
    ),
    (
        "Any patient birthdays this week?",
        "get_patient_birthdays",
        "Should call get_patient_birthdays with date range",
    ),
    (
        "How much did we collect this month?",
        "get_collection_summary",
        "Should call get_collection_summary",
    ),
    (
        "Which patients have outstanding balances over $500?",
        "get_open_balances",
        "Should call get_open_balances with min_amount",
    ),
    (
        "Look up John Smith's next appointment",
        "search_patient",
        "Should call search_patient with name",
    ),
]


async def test_data_endpoint(question: str, expected_tool: str, desc: str, client: httpx.AsyncClient) -> dict:
    """Send a question to /api/chat/data and return result info."""
    payload = {
        "tenant": "chirocloud",
        "account_number": "12345",
        "token": "test-jwt-token",
        "message": question,
    }

    try:
        resp = await client.post(f"{API_BASE}/api/chat/data", json=payload, timeout=60.0)
        data = resp.json()

        return {
            "question": question,
            "expected_tool": expected_tool,
            "description": desc,
            "status_code": resp.status_code,
            "reply": data.get("reply", ""),
            "success": resp.status_code == 200 and len(data.get("reply", "")) > 10,
            "error": None,
        }
    except Exception as e:
        return {
            "question": question,
            "expected_tool": expected_tool,
            "description": desc,
            "status_code": None,
            "reply": "",
            "success": False,
            "error": str(e),
        }


async def run_tests():
    print("=" * 70)
    print("SageDocs Data Mode — End-to-End Test")
    print("=" * 70)

    # Pre-check: is SageDocs running?
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(f"{API_BASE}/health", timeout=5.0)
            if r.status_code != 200:
                print(f"\nERROR: SageDocs not healthy at {API_BASE}")
                sys.exit(1)
            print(f"\nSageDocs backend: OK ({API_BASE})")
        except Exception:
            print(f"\nERROR: Cannot reach SageDocs at {API_BASE}")
            print("Start it with: uvicorn app.main:app --port 8500")
            sys.exit(1)

        # Pre-check: is mock ChiroCloud running?
        try:
            r = await client.get("http://localhost:8200/docs", timeout=5.0)
            print("Mock ChiroCloud: OK (http://localhost:8200)")
        except Exception:
            print("\nERROR: Cannot reach Mock ChiroCloud at http://localhost:8200")
            print("Start it with: python tests/mock_chirocloud.py")
            sys.exit(1)

    print(f"\nRunning {len(TEST_CASES)} test cases...\n")

    results = []
    async with httpx.AsyncClient() as client:
        for i, (question, expected_tool, desc) in enumerate(TEST_CASES, 1):
            print(f"[{i}/{len(TEST_CASES)}] {desc}")
            print(f"  Q: {question}")

            result = await test_data_endpoint(question, expected_tool, desc, client)
            results.append(result)

            if result["success"]:
                # Truncate long replies for display
                reply_preview = result["reply"][:150] + "..." if len(result["reply"]) > 150 else result["reply"]
                print(f"  A: {reply_preview}")
                print(f"  PASS")
            else:
                error_detail = result.get('error') or f"HTTP {result['status_code']}"
                print(f"  FAIL: {error_detail}")
                if result["reply"]:
                    print(f"  Reply: {result['reply'][:200]}")
            print()

    # Summary
    passed = sum(1 for r in results if r["success"])
    failed = len(results) - passed

    print("=" * 70)
    print(f"Results: {passed}/{len(results)} passed, {failed} failed")
    print("=" * 70)

    if failed > 0:
        print("\nFailed tests:")
        for r in results:
            if not r["success"]:
                print(f"  - {r['question']}: {r.get('error', 'no reply')}")

    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(run_tests())
    sys.exit(0 if success else 1)
