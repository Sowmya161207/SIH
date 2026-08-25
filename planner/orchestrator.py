"""
Orchestrator: Executes an ExecutionPlan sequentially, passing context from tool to tool,
aggregating source citations, enforcing evidence verification, and producing the final ChatResponse.
"""

import json
import logging
from typing import Optional, List, Dict, Any

from .schemas import (
    ExecutionPlan,
    PlanStep,
    SourceMetadata,
    EvidenceItem,
    VerificationResult,
    ChatResponse,
    RAGResult
)
from .interfaces import (
    BaseRAGAgent,
    BaseVisionAgent,
    BaseAnalyticsAgent,
    BaseEvidenceVerifier,
    BaseLLMAgent,
    BaseWebSearchAgent
)
from .adapters import (
    MockRAGAgent,
    MockVisionAgent,
    MockAnalyticsAgent,
    MockEvidenceVerifier,
    MockLLMAgent,
    MockWebSearchAgent
)

logger = logging.getLogger(__name__)


class OrchestrationError(Exception):
    """Base exception for runtime orchestration failures."""
    pass


class Orchestrator:
    """
    Lightweight orchestration engine that executes an ExecutionPlan.
    Coordinates RAG, Vision, Analytics, Evidence Verification, and LLM synthesis.
    """

    def __init__(
        self,
        rag_agent: Optional[BaseRAGAgent] = None,
        vision_agent: Optional[BaseVisionAgent] = None,
        analytics_agent: Optional[BaseAnalyticsAgent] = None,
        verifier: Optional[BaseEvidenceVerifier] = None,
        llm_agent: Optional[BaseLLMAgent] = None,
        web_search_agent: Optional[BaseWebSearchAgent] = None
    ):
        """
        :param rag_agent: Concrete implementation of BaseRAGAgent.
        :param vision_agent: Concrete implementation of BaseVisionAgent.
        :param analytics_agent: Concrete implementation of BaseAnalyticsAgent.
        :param verifier: Concrete implementation of BaseEvidenceVerifier (hallucination guard).
        :param llm_agent: Concrete implementation of BaseLLMAgent.
        :param web_search_agent: Concrete implementation of BaseWebSearchAgent.
        """
        self.rag_agent = rag_agent or MockRAGAgent()
        self.vision_agent = vision_agent or MockVisionAgent()
        self.analytics_agent = analytics_agent or MockAnalyticsAgent()
        self.verifier = verifier or MockEvidenceVerifier()
        self.llm_agent = llm_agent or MockLLMAgent()
        self.web_search_agent = web_search_agent or MockWebSearchAgent()

    async def execute_plan(
        self,
        plan: ExecutionPlan,
        original_query: str,
        conversation_id: Optional[str] = None,
        document_ids: Optional[List[str]] = None,
        user_role: Optional[str] = None
    ) -> ChatResponse:
        """
        Executes each step of the ExecutionPlan sequentially, threading context between steps
        and validating evidence grounding before generating final output.

        :param plan: The ExecutionPlan produced by PlannerService.
        :param original_query: The original user question.
        :param conversation_id: Optional conversation identifier.
        :param document_ids: Optional list of document IDs to focus RAG search.
        :param user_role: Optional user access role for RAG permissions.
        :return: ChatResponse containing answer, status, confidence, evidence, sources, and plan.
        """
        # When plan action/intent is clarification, return immediately without calling tools
        if plan.intent == "clarification" or any(s.action == "clarify" for s in plan.steps):
            return ChatResponse(
                status="clarification",
                answer="Could you clarify what you would like me to explain further?",
                conversation_id=conversation_id,
                sources=[],
                evidence=[],
                confidence=1.0,
                steps=plan.steps,
                plan=plan
            )

        context_buffer: List[str] = []
        collected_sources: List[SourceMetadata] = []
        collected_evidence: List[EvidenceItem] = []
        overall_confidence: float = 1.0
        final_answer: str = ""

        try:
            for step in plan.steps:
                logger.info(f"Executing step {step.step}: tool={step.tool}, action={step.action}")

                if step.tool == "rag":
                    # Call RAG tool via clean search_documents interface
                    rag_result: RAGResult = await self.rag_agent.search_documents(
                        query=step.input if step.input and step.input != original_query else original_query,
                        user_role=user_role,
                        document_ids=document_ids
                    )
                    # Extract text chunks and structure evidence items
                    for chunk in rag_result.chunks:
                        context_buffer.append(chunk.text)
                        collected_evidence.append(
                            EvidenceItem(
                                source_type="document",
                                title=chunk.source.document,
                                content=chunk.text,
                                page=chunk.source.page,
                                confidence=chunk.source.score or 0.90,
                                metadata={"chunk_id": chunk.source.chunk_id}
                            )
                        )

                    # Accumulate and deduplicate sources
                    for src in rag_result.sources:
                        if not self._is_source_present(collected_sources, src):
                            collected_sources.append(src)

                elif step.tool == "vision":
                    # Call Vision / Multimodal tool interface
                    vision_result: Dict[str, Any] = await self.vision_agent.analyze_image(
                        query=original_query
                    )
                    desc = vision_result.get("description", "")
                    if desc:
                        context_buffer.append(desc)
                    collected_evidence.append(
                        EvidenceItem(
                            source_type="vision",
                            title=vision_result.get("image_id", "engineering_diagram.svg"),
                            content=desc or "Visual features detected",
                            confidence=vision_result.get("confidence", 0.95),
                            metadata=vision_result
                        )
                    )

                elif step.tool == "analytics":
                    # Call Data Analytics / Maintenance Telemetry interface
                    analytics_result: Dict[str, Any] = await self.analytics_agent.get_maintenance_analytics(
                        query=step.input or original_query
                    )
                    formatted_analytics = json.dumps(analytics_result)
                    context_buffer.append(f"Telemetry Analytics: {formatted_analytics}")
                    collected_evidence.append(
                        EvidenceItem(
                            source_type="analytics",
                            title=f"Telemetry {analytics_result.get('equipment_id', 'Asset')}",
                            content=formatted_analytics,
                            confidence=analytics_result.get("confidence", 0.95),
                            metadata=analytics_result
                        )
                    )

                elif step.tool == "verify":
                    # Call Evidence Verification Agent (Hallucination Guard)
                    verification: VerificationResult = await self.verifier.verify_evidence(
                        query=original_query,
                        evidence=collected_evidence
                    )
                    overall_confidence = verification.confidence
                    if not verification.is_sufficient:
                        logger.warning(f"Evidence verification failed: {verification.reason}")
                        return ChatResponse(
                            status="insufficient_evidence",
                            answer="I cannot answer this question with high certainty because sufficient supporting evidence was not found in the on-premise knowledge repository.",
                            conversation_id=conversation_id,
                            sources=[],
                            evidence=[],
                            confidence=0.0,
                            reason=verification.reason or "Insufficient verified evidence.",
                            steps=plan.steps,
                            plan=plan
                        )

                elif step.tool == "web_search":
                    web_snippets = await self.web_search_agent.search(
                        query=original_query
                    )
                    for snip in web_snippets:
                        context_buffer.append(snip)
                        collected_evidence.append(
                            EvidenceItem(
                                source_type="web",
                                title="Web Search Result",
                                content=snip,
                                confidence=0.85
                            )
                        )

                elif step.tool == "llm":
                    # Pass clean original user query + verified context buffer to LLM
                    answer = await self.llm_agent.generate(
                        prompt=original_query,
                        context=context_buffer if context_buffer else None,
                        system_instruction=f"Action: {step.action}."
                    )
                    final_answer = answer

                else:
                    raise OrchestrationError(f"Unsupported tool '{step.tool}' at step {step.step}")

            # Hallucination Guard: Check if private retrieval was required but no evidence was found
            if (plan.requires_rag or plan.intent in ("incident_investigation", "maintenance_analytics", "multimodal_qa")) and not collected_evidence:
                return ChatResponse(
                    status="insufficient_evidence",
                    answer="I cannot answer this question because no relevant documents, telemetry, or diagrams were found in the knowledge repository.",
                    conversation_id=conversation_id,
                    sources=[],
                    evidence=[],
                    confidence=0.0,
                    reason="No matching evidence found in on-premise knowledge repository.",
                    steps=plan.steps,
                    plan=plan
                )

            if not final_answer:
                final_answer = "No response could be generated for the given plan."

            return ChatResponse(
                status="success",
                answer=final_answer,
                conversation_id=conversation_id,
                sources=collected_sources,
                evidence=collected_evidence,
                confidence=overall_confidence,
                steps=plan.steps,
                plan=plan
            )

        except Exception as e:
            logger.error(f"Orchestration execution failed: {e}", exc_info=True)
            raise OrchestrationError(f"Execution failed during plan processing: {str(e)}") from e

    def _is_source_present(self, source_list: List[SourceMetadata], candidate: SourceMetadata) -> bool:
        """Helper to deduplicate citations based on document name and page number."""
        for s in source_list:
            if s.document == candidate.document and s.page == candidate.page:
                return True
        return False


