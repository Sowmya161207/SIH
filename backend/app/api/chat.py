from fastapi import APIRouter, status
from app.models.chat import ChatRequest, ChatResponse
from app.services.chat_service import chat_service

router = APIRouter(tags=["Chat"])


@router.post(
    "/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Process chat message",
    description="Send a message to the assistant and receive a response with source citations."
)
async def chat(request: ChatRequest) -> ChatResponse:
    """Process incoming chat message using ChatService."""
    return await chat_service.process_message(request)
