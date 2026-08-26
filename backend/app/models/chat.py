from typing import List, Optional
from pydantic import BaseModel, field_validator


class ChatRequest(BaseModel):
    """Chat API request contract."""

    message: str
    conversation_id: Optional[str] = None
    document_id: Optional[str] = None
    attached_filename: Optional[str] = None

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Message cannot be empty or whitespace-only.")
        return v.strip()


class Source(BaseModel):
    """Source provenance model for RAG integration."""

    document: str
    page: Optional[int] = None


class ChatResponse(BaseModel):
    """Chat API response contract."""

    answer: str
    conversation_id: Optional[str] = None
    sources: List[Source] = []
