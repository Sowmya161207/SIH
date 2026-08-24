"""
Unit tests for the Orchestrator.
Verifies step execution, context passing, and source metadata propagation.
"""

import asyncio
import pytest
from planner.schemas import ExecutionPlan, PlanStep, SourceMetadata
from planner.orchestrator import Orchestrator, OrchestrationError
from planner.adapters import MockRAGAgent, MockLLMAgent, MockWebSearchAgent


def test_orchestrator_general_qa_execution():
    """Tests executing a single-step LLM plan without RAG context."""
    async def _run():
        orchestrator = Orchestrator()
        plan = ExecutionPlan(
            intent="general_qa",
            requires_rag=False,
            requires_web=False,
            steps=[
                PlanStep(step=1, tool="llm", action="answer", input="What is artificial intelligence?")
            ]
        )

        response = await orchestrator.execute_plan(
            plan=plan,
            original_query="What is artificial intelligence?",
            conversation_id="conv-123"
        )

        assert response.conversation_id == "conv-123"
        assert "Artificial Intelligence" in response.answer
        assert len(response.sources) == 0
        assert response.plan == plan

    asyncio.run(_run())


def test_orchestrator_rag_context_and_sources_flow():
    """Tests that RAG retrieved chunks are passed into the LLM and source metadata is preserved."""
    async def _run():
        rag_agent = MockRAGAgent(sample_document="cybersecurity_whitepaper.pdf", sample_page=7)
        llm_agent = MockLLMAgent()
        orchestrator = Orchestrator(rag_agent=rag_agent, llm_agent=llm_agent)

        plan = ExecutionPlan(
            intent="document_qa",
            requires_rag=True,
            requires_web=False,
            steps=[
                PlanStep(step=1, tool="rag", action="retrieve", input="Retrieve zero-trust policy."),
                PlanStep(step=2, tool="llm", action="synthesize", input="Summarize zero-trust policy.")
            ]
        )

        response = await orchestrator.execute_plan(
            plan=plan,
            original_query="What is the zero-trust policy in the PDF?",
            conversation_id="conv-456",
            document_ids=["cybersecurity_whitepaper.pdf"]
        )

        assert response.conversation_id == "conv-456"
        assert "zero-trust" in response.answer
        assert len(response.sources) >= 1
        assert response.sources[0].document == "cybersecurity_whitepaper.pdf"
        assert response.sources[0].page == 7

    asyncio.run(_run())


def test_orchestrator_source_deduplication():
    """Tests that duplicate source citations across multiple chunks are deduplicated."""
    orchestrator = Orchestrator()
    
    s1 = SourceMetadata(document="doc1.pdf", page=1)
    s2 = SourceMetadata(document="doc1.pdf", page=1) # duplicate
    s3 = SourceMetadata(document="doc1.pdf", page=2) # different page
    
    unique_list = []
    for s in [s1, s2, s3]:
        if not orchestrator._is_source_present(unique_list, s):
            unique_list.append(s)

    assert len(unique_list) == 2
    assert unique_list[0].page == 1
    assert unique_list[1].page == 2
