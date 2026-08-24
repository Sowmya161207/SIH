import logging
from app.models.chat import ChatRequest, ChatResponse, Source
from app.services.rag_service import retrieve

logger = logging.getLogger(__name__)


class ChatService:
    """Service handling chat interactions and RAG evidence retrieval."""

    async def process_message(self, request: ChatRequest) -> ChatResponse:
        """Process chat message and return response with RAG source citations."""
        logger.info(f"Processing chat request. Conversation ID: {request.conversation_id}")

        evidence_list = retrieve(query=request.message, top_k=5)

        # Filter evidence with significant similarity (> 0.40)
        strong_evidence = [e for e in evidence_list if e.get("score", 0.0) >= 0.40]

        sources = []
        seen_sources = set()
        for ev in strong_evidence:
            doc_name = ev.get("source") or ev.get("document_id", "unknown.pdf")
            page_num = ev.get("page", 1)
            key = (doc_name, page_num)
            if key not in seen_sources:
                sources.append(Source(document=doc_name, page=page_num))
                seen_sources.add(key)

        if strong_evidence:
            first_ev = strong_evidence[0]
            answer = (
                f"Based on retrieved document '{first_ev.get('source')}' (Page {first_ev.get('page')}): "
                f"\"{first_ev.get('content')[:180]}...\""
            )
        else:
            answer = "This is a mock response from the Sovereign AI Workbench."

        return ChatResponse(
            answer=answer,
            conversation_id=request.conversation_id,
            sources=sources
        )


chat_service = ChatService()
