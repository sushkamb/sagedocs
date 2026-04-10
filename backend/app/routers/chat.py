import json
import logging
import os
import uuid

from fastapi import APIRouter, Header, HTTPException, Request
from fastapi.responses import JSONResponse

from app.models.schemas import ChatRequest, ChatResponse
from app.services.rag_engine import RAGEngine
from app.services.query_engine import QueryEngine
from app.routers.analytics import log_question
from app.auth import validate_widget_access, validate_widget_api_key, build_csp_header

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["Chat"])

rag_engine = RAGEngine()
query_engine = QueryEngine()

TENANTS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "tenants")


def _load_and_validate_tenant(tenant_id: str, origin: str | None, widget_key: str | None) -> dict:
    """Load tenant config and validate widget access. Returns tenant data dict."""
    path = os.path.join(TENANTS_DIR, f"{tenant_id}.json")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"Tenant '{tenant_id}' not found")

    with open(path, "r") as f:
        data = json.load(f)

    origin_error = validate_widget_access(data, origin)
    if origin_error:
        raise HTTPException(status_code=403, detail=origin_error)

    key_error = validate_widget_api_key(data, widget_key)
    if key_error:
        raise HTTPException(status_code=401, detail=key_error)

    return data


@router.post("/")
async def chat(request: ChatRequest, req: Request, x_widget_key: str | None = Header(None)):
    """Main chat endpoint — routes to help mode or data mode based on intent."""

    origin = req.headers.get("origin")
    tenant_data = _load_and_validate_tenant(request.tenant, origin, x_widget_key)

    session_id = request.session_id or str(uuid.uuid4())
    logger.info("Chat request: tenant=%s mode=%s message=%r",
                request.tenant,
                "unified" if (request.account_number and request.token) else "help",
                request.message[:120])

    if request.account_number and request.token:
        result = await _unified_chat(request)
    else:
        result = rag_engine.query(request.tenant, request.message)

    answered = bool(result.get("sources")) or bool(result.get("reply"))
    log_question(request.tenant, request.message, answered)

    logger.info("Chat response: answered=%s sources=%d reply_len=%d",
                answered, len(result.get("sources", [])), len(result.get("reply", "")))

    response = JSONResponse(content={
        "reply": result["reply"],
        "sources": result.get("sources", []),
        "images": result.get("images", []),
        "session_id": session_id,
    })

    csp = build_csp_header(tenant_data)
    if csp:
        response.headers["Content-Security-Policy"] = csp

    return response


@router.post("/help")
async def chat_help(request: ChatRequest, req: Request, x_widget_key: str | None = Header(None)):
    """Help mode only — answers from documentation."""

    origin = req.headers.get("origin")
    tenant_data = _load_and_validate_tenant(request.tenant, origin, x_widget_key)

    session_id = request.session_id or str(uuid.uuid4())
    result = rag_engine.query(request.tenant, request.message)

    answered = bool(result.get("sources"))
    log_question(request.tenant, request.message, answered)

    response = JSONResponse(content={
        "reply": result["reply"],
        "sources": result.get("sources", []),
        "images": result.get("images", []),
        "session_id": session_id,
    })

    csp = build_csp_header(tenant_data)
    if csp:
        response.headers["Content-Security-Policy"] = csp

    return response


@router.post("/data")
async def chat_data(request: ChatRequest, req: Request, x_widget_key: str | None = Header(None)):
    """Data mode only — answers by querying host app API."""

    if not request.account_number or not request.token:
        raise HTTPException(status_code=400, detail="account_number and token are required for data queries")

    origin = req.headers.get("origin")
    tenant_data = _load_and_validate_tenant(request.tenant, origin, x_widget_key)

    session_id = request.session_id or str(uuid.uuid4())

    result = await query_engine.query(
        tenant=request.tenant,
        question=request.message,
        account_number=request.account_number,
        token=request.token,
    )

    answered = bool(result.get("reply"))
    log_question(request.tenant, request.message, answered)

    response = JSONResponse(content={
        "reply": result["reply"],
        "sources": result.get("sources", []),
        "images": result.get("images", []),
        "session_id": session_id,
    })

    csp = build_csp_header(tenant_data)
    if csp:
        response.headers["Content-Security-Policy"] = csp

    return response


_NON_ANSWER_PHRASES = [
    "not in the documentation",
    "not in the provided documentation",
    "can't find",
    "cannot find",
    "don't have",
    "do not have",
    "no information",
    "no instructions",
    "not covered",
    "contact support",
    "contact chirocloud support",
]


def _is_non_answer(reply: str) -> bool:
    """Check if a RAG reply is essentially saying 'I don't know'."""
    if len(reply.strip()) < 20:
        return True
    lower = reply.lower()
    # Check if more than 30% of the reply is a non-answer phrase
    for phrase in _NON_ANSWER_PHRASES:
        if phrase in lower:
            return True
    return False


async def _unified_chat(request: ChatRequest) -> dict:
    """Unified chat — tries help mode first, falls back to data mode if needed."""

    # Try help mode first
    logger.info("Unified chat: trying help mode first")
    help_result = rag_engine.query(request.tenant, request.message)

    has_sources = bool(help_result["sources"])
    non_answer = _is_non_answer(help_result["reply"])
    logger.info("Help mode result: sources=%d non_answer=%s", len(help_result.get("sources", [])), non_answer)

    # If help mode found relevant docs AND actually answered, return that
    if has_sources and not non_answer:
        logger.info("Unified chat: returning help mode result")
        return help_result

    # Otherwise try data mode
    logger.info("Unified chat: falling back to data mode (sources=%s, non_answer=%s)", has_sources, non_answer)
    data_result = await query_engine.query(
        tenant=request.tenant,
        question=request.message,
        account_number=request.account_number,
        token=request.token,
    )

    if data_result["reply"]:
        logger.info("Unified chat: returning data mode result")
        return data_result

    # Neither mode could answer
    logger.warning("Unified chat: neither mode could answer for tenant=%s", request.tenant)
    return {
        "reply": "I wasn't able to find an answer to that question. Please try rephrasing or contact support for help.",
        "sources": [],
    }
