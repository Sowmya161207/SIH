from fastapi import APIRouter, Depends, status

from app.core.security import require_role
from app.models.chat import ChatRequest, ChatResponse
from app.services.chat_service import chat_service


router = APIRouter(tags=["Chat"])


@router.post(
    "/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Process chat message",
    description=(
        "Send a message to the assistant and receive a response "
        "with source citations."
    ),
)
async def chat(
    request: ChatRequest,
    current_user: dict = Depends(
    require_role(
        "operator",
        "supervisor",
        "viewer",
        "manager",
        "admin",
    )
),
) -> ChatResponse:
    """
    Process an authenticated chat request.

    The authenticated user's role is passed to ChatService so that
    downstream RAG retrieval can enforce role-based document access.
    """

    return await chat_service.process_message(
        request=request,
        user_role=current_user["role"],
    )