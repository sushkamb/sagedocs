from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ChatRequest(BaseModel):
    tenant: str
    account_number: Optional[str] = None
    token: Optional[str] = None
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    sources: list[dict] = []
    images: list[str] = []
    session_id: str


class DocumentUpload(BaseModel):
    tenant: str
    title: str
    source_type: str = "manual"


class DocumentInfo(BaseModel):
    id: str
    tenant: str
    title: str
    filename: str
    chunk_count: int
    uploaded_at: datetime


class TenantConfig(BaseModel):
    tenant_id: str
    display_name: str
    welcome_message: str = "Hi! How can I help you?"
    placeholder_text: str = "Ask me anything..."
    starter_questions: list[str] = []
    widget_position: str = "bottom-right"
    primary_color: str = "#0066cc"
    logo_url: Optional[str] = None
    help_mode_enabled: bool = True
    data_mode_enabled: bool = False
    llm_model: Optional[str] = None
    system_prompt: Optional[str] = None


class AnalyticsEntry(BaseModel):
    question: str
    tenant: str
    answered: bool
    timestamp: datetime
