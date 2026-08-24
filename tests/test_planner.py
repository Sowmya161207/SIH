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


# ==============================================================================
# SIH PS 26117 Task Routing & Multimodal Capability Tests
# ==============================================================================

def test_task_routing_document_question():
    """
    SIH PS 26117: Text / Document Question Task Routing.
    Input: 'What does the uploaded safety manual say about pressure limits?'
    Expected: task_type='document_qa', requires_text=True, requires_image=False, requires_retrieval=True
    """
    async def _run():
        planner = PlannerService()
        result = await planner.plan("What does the uploaded safety manual say about pressure limits?", conversation_id="sih-001")

        assert result.task_type == "document_qa"
        assert result.action == "rag"
        assert result.requires_text is True
        assert result.requires_image is False
        assert result.requires_retrieval is True
        assert result.retrieval_required is True
        assert result.capability == "text"
        assert result.selected_model == "llama3:8b"

    asyncio.run(_run())


def test_task_routing_image_pid_question():
    """
    SIH PS 26117: Image / P&ID Diagram Question Task Routing.
    Input: 'What valve is connected to the inlet line in the P&ID diagram?'
    Expected: task_type='image_qa', requires_text=False, requires_image=True, requires_retrieval=True
    """
    async def _run():
        planner = PlannerService()
        result = await planner.plan("What valve is connected to the inlet line in the P&ID diagram?", conversation_id="sih-002")

        assert result.task_type == "image_qa"
        assert result.action == "rag"
        assert result.requires_text is False
        assert result.requires_image is True
        assert result.requires_retrieval is True
        assert result.retrieval_required is True
        assert result.capability == "vision"
        assert result.selected_model == "llava:7b"

    asyncio.run(_run())


def test_task_routing_multimodal_question():
    """
    SIH PS 26117: Multimodal Question Task Routing (Text Specs + Diagram/P&ID).
    Input: 'Compare the valve specifications in the PDF with the P&ID diagram drawing.'
    Expected: task_type='multimodal_qa', requires_text=True, requires_image=True, requires_retrieval=True
    """
    async def _run():
        planner = PlannerService()
        result = await planner.plan("Compare the valve specifications in the PDF with the P&ID diagram drawing.", conversation_id="sih-003")

        assert result.task_type == "multimodal_qa"
        assert result.action == "rag"
        assert result.requires_text is True
        assert result.requires_image is True
        assert result.requires_retrieval is True
        assert result.retrieval_required is True
        assert result.capability == "multimodal"
        assert result.selected_model == "qwen-vl:7b"

    asyncio.run(_run())


def test_task_routing_calculation_reasoning():
    """
    SIH PS 26117: Calculation / Quantitative Reasoning Task Routing.
    Input: 'Calculate the pressure drop across the pipe with flow rate 50 m3/h.'
    Expected: task_type='calculation_reasoning', capability='reasoning', requires_text=True, requires_image=False
    """
    async def _run():
        planner = PlannerService()
        result = await planner.plan("Calculate the pressure drop across the pipe with flow rate 50 m3/h.", conversation_id="sih-004")

        assert result.task_type == "calculation_reasoning"
        assert result.requires_text is True
        assert result.requires_image is False
        assert result.capability == "reasoning"
        assert result.selected_model == "qwen2.5-coder:7b"

    asyncio.run(_run())


def test_task_routing_configurable_model_registry():
    """
    SIH PS 26117: Configurable open-weight model capability mapping.
    Ensures models are configurable without hardcoding providers.
    """
    async def _run():
        custom_registry = {
            "text": "mistral:instruct",
            "vision": "qwen2-vl:7b",
            "reasoning": "deepseek-coder:6.7b"
        }
        planner = PlannerService(model_registry=custom_registry)

        doc_res = await planner.plan("Summarize the uploaded document.")
        assert doc_res.selected_model == "mistral:instruct"

        vision_res = await planner.plan("Inspect valve tag on the P&ID blueprint.")
        assert vision_res.selected_model == "qwen2-vl:7b"

        calc_res = await planner.plan("Calculate heat duty for exchanger E-101.")
        assert calc_res.selected_model == "deepseek-coder:6.7b"

    asyncio.run(_run())


def test_task_routing_safe_failure_on_invalid_input():
    """
    SIH PS 26117: Robust error handling and safe failure.
    Planner fails safely and gracefully returns clarification without crashing backend.
    """
    async def _run():
        planner = PlannerService()

        # None / whitespace
        res1 = await planner.plan("")
        assert res1.task_type == "clarification"
        assert res1.action == "clarification"

        res2 = await planner.plan("    \n\t  ")
        assert res2.task_type == "clarification"
        assert res2.action == "clarification"

    asyncio.run(_run())


# ==============================================================================
# SIH 26117 SPECIFIC EXAMPLES & DECISION CONTRACT TESTS
# ==============================================================================

def test_sih_example_1_pump_sop_query():
    """
    Example 1: 'What does the Pump P-101 SOP say?'
    Expected: action='rag', requires_retrieval=True, requires_analytics=False,
              requires_vision=False, requires_generation=True, explainable reason.
    """
    async def _run():
        from planner import plan_query
        decision = await plan_query("What does the Pump P-101 SOP say?", conversation_id="conv-sop")

        assert decision.action == "rag"
        assert decision.requires_retrieval is True
        assert decision.requires_analytics is False
        assert decision.requires_vision is False
        assert decision.requires_generation is True
        assert decision.task_type == "document_qa"
        assert "rag" in decision.selected_tools
        assert "llm" in decision.selected_tools
        assert "SOP" in decision.reason or "documents" in decision.reason

    asyncio.run(_run())


def test_sih_example_2_abnormal_vibration_query():
    """
    Example 2: 'Is Pump P-101 showing abnormal vibration?'
    Expected: action='analytics', requires_retrieval=False, requires_analytics=True,
              requires_vision=False, requires_generation=True, explainable reason.
    """
    async def _run():
        from planner import plan_query
        decision = await plan_query("Is Pump P-101 showing abnormal vibration?", conversation_id="conv-vib")

        assert decision.action == "analytics"
        assert decision.requires_analytics is True
        assert decision.requires_retrieval is False
        assert decision.requires_vision is False
        assert decision.requires_generation is True
        assert decision.task_type == "analytics_qa"
        assert "analytics" in decision.selected_tools
        assert "vibration" in decision.reason or "telemetry" in decision.reason

    asyncio.run(_run())


def test_sih_example_3_pid_diagram_query():
    """
    Example 3: 'What is shown in this P&ID?'
    Expected: requires_vision=True, requires_analytics=False, requires_generation=True, explainable reason.
    """
    async def _run():
        from planner import plan_query
        decision = await plan_query("What is shown in this P&ID?", conversation_id="conv-pid")

        assert decision.requires_vision is True
        assert decision.requires_analytics is False
        assert decision.requires_generation is True
        assert decision.capability == "vision"
        assert decision.selected_model == "llava:7b"
        assert "P&ID" in decision.reason or "diagram" in decision.reason

    asyncio.run(_run())


def test_sih_example_4_multi_tool_risk_query():
    """
    Example 4: 'Why is Pump P-101 at risk and what should we do?'
    Expected: requires_retrieval=True, requires_analytics=True, requires_vision=False,
              requires_generation=True, multi-tool plan with RAG + Analytics + Verify + LLM.
    """
    async def _run():
        from planner import plan_query
        decision = await plan_query("Why is Pump P-101 at risk and what should we do?", conversation_id="conv-risk")

        assert decision.requires_retrieval is True
        assert decision.requires_analytics is True
        assert decision.requires_generation is True
        assert decision.task_type == "incident_investigation"
        assert "rag" in decision.selected_tools
        assert "analytics" in decision.selected_tools
        assert "verify" in decision.selected_tools
        assert "llm" in decision.selected_tools
        assert "telemetry" in decision.reason or "procedures" in decision.reason

    asyncio.run(_run())


def test_planner_tool_availability_fallback():
    """
    Test fallback behavior when a required tool (e.g. analytics) is unavailable.
    """
    async def _run():
        from planner import plan_query
        # Analytics tool is unavailable (only rag and llm online)
        decision = await plan_query(
            "Is Pump P-101 showing abnormal vibration?",
            available_tools=["rag", "llm"]
        )

        assert decision.fallback_action == "direct_llm"
        assert "unavailable" in decision.reason
        assert decision.requires_analytics is False

    asyncio.run(_run())


def test_planner_user_context_and_security():
    """
    Test that user and workspace security context is preserved and respected.
    """
    async def _run():
        from planner import plan_query
        user_ctx = {
            "user_role": "field_operator",
            "workspace_id": "plant_section_4",
            "allowed_documents": ["p101_sop.pdf"]
        }
        decision = await plan_query(
            "What does the Pump P-101 SOP say?",
            user_context=user_ctx
        )

        assert decision.user_context == user_ctx
        assert decision.user_context["user_role"] == "field_operator"
        assert decision.requires_retrieval is True

    asyncio.run(_run())



