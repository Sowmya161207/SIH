import logging
from app.models.chat import ChatRequest, ChatResponse

logger = logging.getLogger(__name__)


class ChatService:
    """Service handling chat interactions and assistant response generation."""

    async def process_message(self, request: ChatRequest) -> ChatResponse:
        """Process chat message and return formatted response."""
        logger.info(f"Processing chat request. Conversation ID: {request.conversation_id}")

        # Currently returns a mock response.
        # Future phases will integrate AI Planner -> RAG -> LLM pipeline here.
        mock_answer = "This is a mock response from the Sovereign AI Workbench."

        return ChatResponse(
            answer=mock_answer,
            conversation_id=request.conversation_id,
            sources=[]
        )


chat_service = ChatService()
