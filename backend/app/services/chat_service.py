import logging
from typing import Optional

from app.models.chat import ChatRequest, ChatResponse, Source
from app.services.llm_service import generate_answer
from app.services.rag_service import retrieve


logger = logging.getLogger(__name__)


class ChatService:
    """
    Service handling authenticated chat requests using:

    JWT user role
        ↓
    Role-aware RAG retrieval
        ↓
    Evidence filtering
        ↓
    Local Ollama LLM
        ↓
    Source citations
    """

    async def process_message(
        self,
        request: ChatRequest,
        user_role: Optional[str] = None,
    ) -> ChatResponse:
        """
        Retrieve grounded evidence and generate a local LLM answer.

        Parameters
        ----------
        request:
            Incoming chat request.

        user_role:
            Role extracted from the authenticated JWT.
            This is passed to RAG so document ACLs can be enforced.
        """

        logger.info(
            "Processing chat request | conversation_id=%s | role=%s",
            request.conversation_id,
            user_role,
        )

        try:
            # ---------------------------------------------------------
            # STEP 1: Retrieve evidence using role-aware RAG
            # ---------------------------------------------------------

            # General evidence from company documents (top 3 is enough for concise answers)
            company_evidence = retrieve(
                query=request.message,
                top_k=3,
                user_role=user_role,
            )

            # Specific evidence from user's attached document / image if provided
            query_doc_evidence = []
            if getattr(request, "document_id", None):
                query_doc_evidence = retrieve(
                    query=request.message,
                    document_ids=[request.document_id],
                    top_k=3,
                    user_role=user_role,
                )

            # Combine evidence (avoiding duplicates)
            seen_ids = set()
            evidence_list = []
            for item in query_doc_evidence + company_evidence:
                item_id = (item.get("document_id"), item.get("page"), item.get("content", "")[:30])
                if item_id not in seen_ids:
                    seen_ids.add(item_id)
                    evidence_list.append(item)

            logger.info(
                "RAG returned %d evidence items (company: %d, query_doc: %d) for role=%s",
                len(evidence_list),
                len(company_evidence),
                len(query_doc_evidence),
                user_role,
            )

            # ---------------------------------------------------------
            # STEP 2: Filter low-confidence evidence
            # ---------------------------------------------------------

            strong_evidence = [
                evidence
                for evidence in evidence_list
                if evidence.get("score", 0.0) >= 0.20 or evidence.get("document_id") == getattr(request, "document_id", None)
            ]

            if not strong_evidence:
                strong_evidence = evidence_list[:3]

            # Sort by score descending so LLM receives strongest evidence first
            strong_evidence = sorted(
                strong_evidence,
                key=lambda e: e.get("score", 0.0),
                reverse=True,
            )

            logger.info(
                "Strong evidence after confidence filtering: %d",
                len(strong_evidence),
            )

            # ---------------------------------------------------------
            # STEP 3: Handle insufficient evidence
            # ---------------------------------------------------------

            if not strong_evidence:
                return ChatResponse(
                    answer=(
                        "I could not find sufficient evidence in the "
                        "documents available to your role to answer "
                        "this question."
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