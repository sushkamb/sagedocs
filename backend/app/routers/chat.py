import uuid
from fastapi import APIRouter, HTTPException

from app.models.schemas import ChatRequest, ChatResponse
from app.services.rag_engine import RAGEngine
from app.services.query_engine import QueryEngine

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

    return ChatResponse(
        reply=result["reply"],
        sources=result.get("sources", []),
        session_id=session_id,
    )


@router.post("/help", response_model=ChatResponse)
async def chat_help(request: ChatRequest):
    """Help mode only — answers from documentation."""

    session_id = request.session_id or str(uuid.uuid4())
    result = rag_engine.query(request.tenant, request.message)

    return ChatResponse(
        reply=result["reply"],
        sources=result.get("sources", []),
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

    return ChatResponse(
        reply=result["reply"],
        sources=result.get("sources", []),
        session_id=session_id,
    )


async def _unified_chat(request: ChatRequest) -> dict:
    """Unified chat — tries help mode first, falls back to data mode if needed."""

    # Try help mode first
    help_result = rag_engine.query(request.tenant, request.message)

    # If help mode found relevant docs, return that answer
    if help_result["sources"]:
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
