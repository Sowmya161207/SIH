import logging

from app.models.chat import ChatRequest, ChatResponse, Source
from app.services.llm_service import generate_answer
from app.services.rag_service import retrieve

logger = logging.getLogger(__name__)


class ChatService:
    """Service handling chat using improved RAG and local Ollama LLM."""

    async def process_message(
        self,
        request: ChatRequest,
    ) -> ChatResponse:
        """Retrieve grounded evidence and generate a local LLM answer."""

        logger.info(
            "Processing chat request. Conversation ID: %s",
            request.conversation_id,
        )

        try:
            # ---------------------------------------------------------
            # STEP 1: Retrieve evidence using the improved RAG pipeline
            # ---------------------------------------------------------

            evidence_list = retrieve(
                query=request.message,
                top_k=5,
            )

            # ---------------------------------------------------------
            # STEP 2: Filter low-confidence evidence
            # ---------------------------------------------------------

            strong_evidence = [
                evidence
                for evidence in evidence_list
                if evidence.get("score", 0.0) >= 0.40
            ]

            # ---------------------------------------------------------
            # STEP 3: Handle insufficient evidence
            # ---------------------------------------------------------

            if not strong_evidence:
                return ChatResponse(
                    answer=(
                        "I could not find sufficient evidence in the "
                        "available documents to answer this question."
                    ),
                    conversation_id=request.conversation_id,
                    sources=[],
                )

            # ---------------------------------------------------------
            # STEP 4: Generate grounded answer using local Ollama
            # ---------------------------------------------------------

            answer = await generate_answer(
                question=request.message,
                evidence=strong_evidence,
            )

            # ---------------------------------------------------------
            # STEP 5: Build source/provenance information
            # ---------------------------------------------------------

            sources = []
            seen_sources = set()

            for evidence in strong_evidence:
                document = evidence.get(
                    "source",
                    evidence.get(
                        "title",
                        evidence.get(
                            "document_id",
                            "Unknown document",
                        ),
                    ),
                )

                page = evidence.get("page")

                key = (document, page)

                if key in seen_sources:
                    continue

                seen_sources.add(key)

                sources.append(
                    Source(
                        document=document,
                        page=page,
                    )
                )

            # ---------------------------------------------------------
            # STEP 6: Return grounded answer + citations
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