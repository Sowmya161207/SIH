"""
Unit tests for PlannerService and ExecutionPlan generation.
Verifies all test cases specified in the project requirements.
"""

import asyncio
import pytest
from planner.planner_service import (
    PlannerService,
    PlannerValidationError,
    PlannerExecutionError
)
from planner.adapters import MockPlannerLLMClient
from planner.schemas import ExecutionPlan


def test_case_1_general_question():
    """
    Test 1: General knowledge question
    Input: 'What is artificial intelligence?'
    Expected: LLM only, requires_rag=False
    """
    async def _run():
        planner = PlannerService()
        plan: ExecutionPlan = await planner.create_plan("What is artificial intelligence?")

        assert plan.requires_rag is False
        assert plan.requires_web is False
        assert plan.intent == "general_qa"
        assert len(plan.steps) == 1
        assert plan.steps[0].tool == "llm"
        assert plan.steps[0].action == "answer"

    asyncio.run(_run())


def test_case_2_document_question():
    """
    Test 2: Document question
    Input: 'What security mechanisms are mentioned in the uploaded PDF?'
    Expected: RAG -> LLM, requires_rag=True
    """
    async def _run():
        planner = PlannerService()
        plan: ExecutionPlan = await planner.create_plan("What security mechanisms are mentioned in the uploaded PDF?")

        assert plan.requires_rag is True
        assert plan.intent == "document_qa"
        assert len(plan.steps) == 2
        assert plan.steps[0].tool == "rag"
        assert plan.steps[0].action == "retrieve"
        assert plan.steps[1].tool == "llm"
        assert plan.steps[1].action == "synthesize"

    asyncio.run(_run())


def test_case_3_document_summarization():
    """
    Test 3: Document summarization
    Input: 'Summarize the uploaded document.'
    Expected: RAG -> LLM, requires_rag=True
    """
    async def _run():
        planner = PlannerService()
        plan: ExecutionPlan = await planner.create_plan("Summarize the uploaded document.")

        assert plan.requires_rag is True
        assert plan.intent == "document_summarization"
        assert len(plan.steps) == 2
        assert plan.steps[0].tool == "rag"
        assert plan.steps[0].action == "retrieve"
        assert plan.steps[1].tool == "llm"
        assert plan.steps[1].action == "summarize"

    asyncio.run(_run())


def test_case_4_document_comparison():
    """
    Test 4: Document comparison
    Input: 'Compare the two architectures described in the uploaded document.'
    Expected: RAG -> LLM, requires_rag=True
    """
    async def _run():
        planner = PlannerService()
        plan: ExecutionPlan = await planner.create_plan("Compare the two architectures described in the uploaded document.")

        assert plan.requires_rag is True
        assert plan.intent == "document_comparison"
        assert len(plan.steps) == 2
        assert plan.steps[0].tool == "rag"
        assert plan.steps[0].action == "retrieve"
        assert plan.steps[1].tool == "llm"
        assert plan.steps[1].action == "compare"

    asyncio.run(_run())


def test_case_5_current_information():
    """
    Test 5: Current external information / Web search
    Input: 'What are the latest developments in AI?'
    Expected: WEB_SEARCH -> LLM
    """
    async def _run():
        planner = PlannerService()
        plan: ExecutionPlan = await planner.create_plan("What are the latest developments in AI?")

        assert plan.requires_web is True
        assert plan.requires_rag is False
        assert len(plan.steps) == 2
        assert plan.steps[0].tool == "web_search"
        assert plan.steps[0].action == "search"
        assert plan.steps[1].tool == "llm"

    asyncio.run(_run())


def test_case_6_invalid_empty_query():
    """
    Test 6: Empty/whitespace query validation error
    Input: '' or '   '
    Expected: PlannerValidationError
    """
    async def _run():
        planner = PlannerService()

        with pytest.raises(PlannerValidationError):
            await planner.create_plan("")

        with pytest.raises(PlannerValidationError):
            await planner.create_plan("   \n\t  ")

    asyncio.run(_run())


def test_planner_markdown_code_fence_handling():
    """
    Tests that PlannerService correctly extracts JSON even when wrapped in markdown ```json ... ``` blocks.
    """
    async def _run():
        markdown_json = """
        Here is your plan:
        ```json
        {
          "intent": "general_qa",
          "requires_rag": false,
          "requires_web": false,
          "steps": [
            {
              "step": 1,
              "tool": "llm",
              "action": "answer",
              "input": "Explain quantum computing."
            }
          ]
        }
        ```
        Have a nice day!
        """
        mock_client = MockPlannerLLMClient(override_response=markdown_json)
        planner = PlannerService(llm_client=mock_client)
        plan = await planner.create_plan("Explain quantum computing.")

        assert plan.intent == "general_qa"
        assert len(plan.steps) == 1
        assert plan.steps[0].tool == "llm"

    asyncio.run(_run())


def test_planner_invalid_tool_rejection():
    """
    Tests that invalid tools not in the allowed list are rejected by the validator.
    """
    async def _run():
        invalid_tool_json = """
        {
          "intent": "exploit",
          "requires_rag": false,
          "requires_web": false,
          "steps": [
            {
              "step": 1,
              "tool": "bash_shell_executor",
              "action": "run",
              "input": "rm -rf /"
            },
            {
              "step": 2,
              "tool": "llm",
              "action": "answer",
              "input": "Done."
            }
          ]
        }
        """
        mock_client = MockPlannerLLMClient(override_response=invalid_tool_json)
        planner = PlannerService(llm_client=mock_client)

        with pytest.raises(PlannerValidationError) as exc_info:
            await planner.create_plan("Hack system")
        assert "unsupported tool" in str(exc_info.value)

    asyncio.run(_run())


def test_contract_rag_query():
    """
    Contract Test: Document-related query
    Input: 'What does the uploaded document say about X?'
    Expected: action='rag', requires_retrieval=True, requires_generation=True
    """
    async def _run():
        planner = PlannerService()
        result = await planner.plan("What does the uploaded document say about X?", conversation_id="conv-101")

        assert result.action == "rag"
        assert result.requires_retrieval is True
        assert result.requires_generation is True
        assert result.query == "What does the uploaded document say about X?"
        assert result.conversation_id == "conv-101"

    asyncio.run(_run())


def test_contract_general_query():
    """
    Contract Test: General query
    Input: 'What is Python?'
    Expected: action='direct_llm', requires_retrieval=False, requires_generation=True
    """
    async def _run():
        planner = PlannerService()
        result = await planner.plan("What is Python?", conversation_id="conv-102")

        assert result.action == "direct_llm"
        assert result.requires_retrieval is False
        assert result.requires_generation is True
        assert result.query == "What is Python?"
        assert result.conversation_id == "conv-102"

    asyncio.run(_run())


def test_contract_ambiguous_query():
    """
    Contract Test: Ambiguous query
    Input: 'Tell me more.'
    Expected: action='clarification', requires_retrieval=False, requires_generation=False
    """
    async def _run():
        planner = PlannerService()
        result = await planner.plan("Tell me more.", conversation_id="conv-103")

        assert result.action == "clarification"
        assert result.requires_retrieval is False
        assert result.requires_generation is False
        assert result.query == "Tell me more."
        assert result.conversation_id == "conv-103"

    asyncio.run(_run())


def test_contract_empty_query():
    """
    Contract Test: Empty / whitespace query
    Input: '   '
    Expected: action='clarification', requires_retrieval=False, requires_generation=False
    """
    async def _run():
        planner = PlannerService()
        result = await planner.plan("   ", conversation_id="conv-104")

        assert result.action == "clarification"
        assert result.requires_retrieval is False
        assert result.requires_generation is False

    asyncio.run(_run())

