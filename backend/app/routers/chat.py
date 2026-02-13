import uuid
from fastapi import APIRouter, HTTPException

from app.models.schemas import ChatRequest, ChatResponse
from app.services.rag_engine import RAGEngine
from app.services.query_engine import QueryEngine
from app.routers.analytics import log_question

router = APIRouter(prefix="/api/chat", tags=["Chat"])

rag_engine = RAGEngine()
query_engine = QueryEngine()


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint — routes to help mode or data mode based on intent."""

    session_id = request.session_id or str(uuid.uuid4())

    # If data mode is available (account_number + token provided), let the LLM decide
    if request.account_number and request.token:
        result = await _unified_chat(request)
    else:
        # Help mode only
        result = rag_engine.query(request.tenant, request.message)

    answered = bool(result.get("sources")) or bool(result.get("reply"))
    log_question(request.tenant, request.message, answered)

    return ChatResponse(
        reply=result["reply"],
        sources=result.get("sources", []),
        images=result.get("images", []),
        session_id=session_id,
    )


@router.post("/help", response_model=ChatResponse)
async def chat_help(request: ChatRequest):
    """Help mode only — answers from documentation."""

    session_id = request.session_id or str(uuid.uuid4())
    result = rag_engine.query(request.tenant, request.message)

    answered = bool(result.get("sources"))
    log_question(request.tenant, request.message, answered)

    return ChatResponse(
        reply=result["reply"],
        sources=result.get("sources", []),
        images=result.get("images", []),
        session_id=session_id,
    )


@router.post("/data", response_model=ChatResponse)
async def chat_data(request: ChatRequest):
    """Data mode only — answers by querying host app API."""

    if not request.account_number or not request.token:
        raise HTTPException(status_code=400, detail="account_number and token are required for data queries")

    session_id = request.session_id or str(uuid.uuid4())

    result = await query_engine.query(
        tenant=request.tenant,
        question=request.message,
        account_number=request.account_number,
        token=request.token,
    )

    answered = bool(result.get("reply"))
    log_question(request.tenant, request.message, answered)

    return ChatResponse(
        reply=result["reply"],
        sources=result.get("sources", []),
        images=result.get("images", []),
        session_id=session_id,
    )


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
    help_result = rag_engine.query(request.tenant, request.message)

    # If help mode found relevant docs AND actually answered, return that
    if help_result["sources"] and not _is_non_answer(help_result["reply"]):
        return help_result

    # Otherwise try data mode
    data_result = await query_engine.query(
        tenant=request.tenant,
        question=request.message,
        account_number=request.account_number,
        token=request.token,
    )

    if data_result["reply"]:
        return data_result

    # Neither mode could answer
    return {
        "reply": "I wasn't able to find an answer to that question. Please try rephrasing or contact support for help.",
        "sources": [],
    }
