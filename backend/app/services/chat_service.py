import logging
import sys
from pathlib import Path

from app.models.chat import ChatRequest, ChatResponse, Source
from app.services.llm_service import generate_answer
from app.services.model_router import get_available_model

logger = logging.getLogger(__name__)


def _get_rag_search():
    """Load the RAG search function from the project RAG directory."""

    project_root = Path(__file__).resolve().parents[3]
    rag_dir = project_root / "RAG"

    if str(rag_dir) not in sys.path:
        sys.path.insert(0, str(rag_dir))

    from rag_services import search_documents

    return search_documents


class ChatService:
    """Service handling chat interactions using RAG + local Ollama LLM."""

    async def process_message(
        self,
        request: ChatRequest
    ) -> ChatResponse:
        """Retrieve relevant evidence and generate a grounded answer."""

        logger.info(
            "Processing chat request. Conversation ID: %s",
            request.conversation_id,
        )

        try:
            # ---------------------------------------------------------
            # STEP 1: Load RAG search service
            # ---------------------------------------------------------
            search_documents = _get_rag_search()

            # ---------------------------------------------------------
            # STEP 2: Retrieve relevant evidence from ChromaDB
            # ---------------------------------------------------------
            result = search_documents(
                query=request.message,
                top_k=3,
            )

            evidence = result.get("evidence", [])

            # ---------------------------------------------------------
            # STEP 3: Handle no relevant documents
            # ---------------------------------------------------------
            if not evidence:
                return ChatResponse(
                    answer=(
                        "I could not find sufficient evidence in the "
                        "available documents to answer this question."
                    ),
                    conversation_id=request.conversation_id,
                    sources=[],
                )

            # ---------------------------------------------------------
            # STEP 4: Select Model & Generate answer using LOCAL Ollama LLM
            # ---------------------------------------------------------
            selected_model = await get_available_model(intent=None, message=request.message)
            logger.info("ChatService routing request to model: %s", selected_model)

            answer = await generate_answer(
                question=request.message,
                evidence=evidence,
                model=selected_model,
            )

            # ---------------------------------------------------------
            # STEP 5: Build source/provenance information
            # ---------------------------------------------------------
            sources = []

            seen = set()

            for item in evidence:

                document = item.get(
                    "source",
                    item.get(
                        "title",
                        "Unknown document",
                    ),
                )

                page = item.get("page")

                key = (document, page)

                # Avoid duplicate source entries
                if key in seen:
                    continue

                seen.add(key)

                sources.append(
                    Source(
                        document=document,
                        page=page,
                    )
                )

            # ---------------------------------------------------------
            # STEP 6: Return answer + sources to frontend
            # ---------------------------------------------------------
            return ChatResponse(
                answer=answer,
                conversation_id=request.conversation_id,
                sources=sources,
            )

        except Exception as exc:

            logger.exception(
                "RAG + LLM chat processing failed: %s",
                exc,
            )

            return ChatResponse(
                answer=(
                    "I was unable to generate an answer using "
                    "the local AI system. Please try again."
                ),
                conversation_id=request.conversation_id,
                sources=[],
            )


chat_service = ChatService()