import os
import sys
import logging
from app.models.chat import ChatRequest, ChatResponse, Source
from app.core.security import User

# Ensure knowledge and security modules are available
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from knowledge.qa_engine import answer_and_verify
from security.audit import AuditLogger

logger = logging.getLogger(__name__)
audit = AuditLogger()


class ChatService:
    """Service handling chat interactions and assistant response generation."""

    async def process_message(self, request: ChatRequest, user: User) -> ChatResponse:
        """Process chat message and return formatted response."""
        logger.info(f"Processing chat request for user {user.username}. Conversation ID: {request.conversation_id}")

        # Integrate RAG Pipeline with security context
        result = answer_and_verify(
            query=request.message,
            workspace_id=user.workspace_id,
            user_roles=user.roles
        )
        
        # Audit Log
        audit.log_tool_executed("RAG Search", result["search_metadata"]["latency_ms"], caller=user.username)

        sources = []
        for c in result.get("citations", []):
            sources.append(Source(document=c.get("document_title", "Unknown"), page=c.get("page")))

        return ChatResponse(
            answer=result["finding"],
            conversation_id=request.conversation_id,
            sources=sources
        )


chat_service = ChatService()
