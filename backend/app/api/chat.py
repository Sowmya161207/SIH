from fastapi import APIRouter, status, Depends
from app.models.chat import ChatRequest, ChatResponse
from app.services.chat_service import chat_service
from app.core.security import get_current_user, User

router = APIRouter(tags=["Chat"])


@router.post(
    "/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Process chat message",
    description="Send a message to the assistant and receive a response with source citations."
)
async def chat(request: ChatRequest, current_user: User = Depends(get_current_user)) -> ChatResponse:
    """Process incoming chat message using ChatService."""
    return await chat_service.process_message(request, current_user)
