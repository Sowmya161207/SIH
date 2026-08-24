"""
Orchestrator: Executes an ExecutionPlan sequentially, passing context from tool to tool,
aggregating source citations, and producing the final ChatResponse.
"""

import logging
from typing import Optional, List, Dict, Any

from .schemas import (
    ExecutionPlan,
    PlanStep,
    SourceMetadata,
    ChatResponse,
    RAGResult
)
from .interfaces import BaseRAGAgent, BaseLLMAgent, BaseWebSearchAgent
from .adapters import MockRAGAgent, MockLLMAgent, MockWebSearchAgent

logger = logging.getLogger(__name__)


class OrchestrationError(Exception):
    """Base exception for runtime orchestration failures."""
    pass


class Orchestrator:
    """
    Lightweight orchestration engine that executes an ExecutionPlan.
    """

    def __init__(
        self,
        rag_agent: Optional[BaseRAGAgent] = None,
        llm_agent: Optional[BaseLLMAgent] = None,
        web_search_agent: Optional[BaseWebSearchAgent] = None
    ):
        """
        :param rag_agent: Concrete implementation of BaseRAGAgent.
        :param llm_agent: Concrete implementation of BaseLLMAgent.
        :param web_search_agent: Concrete implementation of BaseWebSearchAgent.
        """
        self.rag_agent = rag_agent or MockRAGAgent()
        self.llm_agent = llm_agent or MockLLMAgent()
        self.web_search_agent = web_search_agent or MockWebSearchAgent()

    async def execute_plan(
        self,
        plan: ExecutionPlan,
        original_query: str,
        conversation_id: Optional[str] = None,
        document_ids: Optional[List[str]] = None
    ) -> ChatResponse:
        """
        Executes each step of the ExecutionPlan sequentially, threading context between steps.

        :param plan: The ExecutionPlan produced by PlannerService.
        :param original_query: The original user question.
        :param conversation_id: Optional conversation identifier.
        :param document_ids: Optional list of document IDs to focus RAG search.
        :return: ChatResponse containing answer, conversation_id, sources, and plan.
        """
        # Bug 3 Fix: When plan action/intent is clarification, return immediately without calling RAG/LLM/Web Search
        if plan.intent == "clarification" or any(s.action == "clarify" for s in plan.steps):
            return ChatResponse(
                answer="Could you clarify what you would like me to explain further?",
                conversation_id=conversation_id,
                sources=[],
                plan=plan
            )

        # Maintain lightweight internal execution context
        execution_context: Dict[str, Any] = {
            "user_query": original_query,
            "conversation_id": conversation_id,
            "retrieved_context": [],
            "web_results": [],
            "sources": [],
            "final_answer": None,
        }

        context_buffer: List[str] = []
        collected_sources: List[SourceMetadata] = []
        final_answer: str = ""

        try:
            for step in plan.steps:
                logger.info(f"Executing step {step.step}: tool={step.tool}, action={step.action}")

                if step.tool == "rag":
                    # Bug 1 Fix: Pass clean original_query to RAG (never planner prompts or templates)
                    rag_result: RAGResult = await self.rag_agent.retrieve(
                        query=original_query,
                        document_ids=document_ids
                    )
                    # Extract text chunks into context buffer
                    for chunk in rag_result.chunks:
                        context_buffer.append(chunk.text)
                        execution_context["retrieved_context"].append(chunk.text)
                    
                    # Accumulate and deduplicate sources
                    for src in rag_result.sources:
                        if not self._is_source_present(collected_sources, src):
                            collected_sources.append(src)
                            execution_context["sources"].append(src)

                elif step.tool == "web_search":
                    # Bug 2 Fix: Pass clean original_query to Web Search
                    web_snippets = await self.web_search_agent.search(
                        query=original_query
                    )
                    context_buffer.extend(web_snippets)
                    execution_context["web_results"].extend(web_snippets)

                elif step.tool == "llm":
                    # Pass original user query + retrieved context to LLM
                    answer = await self.llm_agent.generate(
                        prompt=original_query,
                        context=context_buffer if context_buffer else None,
                        system_instruction=f"Action: {step.action}."
                    )
                    final_answer = answer
                    execution_context["final_answer"] = answer

                else:
                    raise OrchestrationError(f"Unsupported tool '{step.tool}' at step {step.step}")

            if not final_answer:
                final_answer = "No response could be generated for the given plan."

            return ChatResponse(
                answer=final_answer,
                conversation_id=conversation_id,
                sources=collected_sources,
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

