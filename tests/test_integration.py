"""
Integration tests for ChatService confirming zero regression and full compatibility
with the backend POST /api/chat contract.
"""

import asyncio
import pytest
from planner.chat_service import ChatService
from planner.schemas import ChatRequest, ChatResponse
from planner.adapters import MockRAGAgent, MockLLMAgent, MockWebSearchAgent


def test_chatservice_general_query_contract():
    """Verifies ChatService returns the exact expected backend contract for general queries."""
    async def _run():
        service = ChatService()
        request = ChatRequest(message="What is artificial intelligence?", conversation_id="sess-001")

        response: ChatResponse = await service.process_chat(request)

        assert isinstance(response, ChatResponse)
        assert response.conversation_id == "sess-001"
        assert response.answer is not None
        assert len(response.answer) > 0
        assert response.sources == []

    asyncio.run(_run())


def test_chatservice_document_query_contract():
    """Verifies ChatService returns the exact expected backend contract with sources for document queries."""
    async def _run():
        service = ChatService()
        request = ChatRequest(message="What security mechanisms are mentioned in the uploaded PDF?", conversation_id="sess-002")

        response: ChatResponse = await service.process_chat(request, document_ids=["policy.pdf"])

        assert isinstance(response, ChatResponse)
        assert response.conversation_id == "sess-002"
        assert len(response.sources) > 0
        assert response.sources[0].document == "policy.pdf"
        assert response.sources[0].page is not None
        assert "zero-trust" in response.answer.lower() or "hardware-backed" in response.answer.lower()

    asyncio.run(_run())


def test_chatservice_empty_query_safe_handling():
    """Verifies that invalid queries produce user-friendly error responses without crashing."""
    async def _run():
        service = ChatService()
        request = ChatRequest(message="   ", conversation_id="sess-003")

        response: ChatResponse = await service.process_chat(request)

        assert isinstance(response, ChatResponse)
        assert response.conversation_id == "sess-003"
        assert "Unable to plan request" in response.answer

    asyncio.run(_run())


# ==============================================================================
# REGRESSION TESTS: Bug 1, Bug 2, Bug 3, Bug 4, Context & Source Propagation
# ==============================================================================

class TrackingRAGAgent(MockRAGAgent):
    def __init__(self):
        super().__init__()
        self.call_count = 0
        self.last_query = None

    async def retrieve(self, query: str, document_ids=None, filters=None):
        self.call_count += 1
        self.last_query = query
        return await super().retrieve(query, document_ids, filters)


class TrackingWebSearchAgent(MockWebSearchAgent):
    def __init__(self):
        super().__init__()
        self.call_count = 0
        self.last_query = None

    async def search(self, query: str, num_results=3):
        self.call_count += 1
        self.last_query = query
        return await super().search(query, num_results)


class TrackingLLMAgent(MockLLMAgent):
    def __init__(self):
        super().__init__()
        self.call_count = 0
        self.last_prompt = None
        self.last_context = None

    async def generate(self, prompt: str, context=None, system_instruction=None):
        self.call_count += 1
        self.last_prompt = prompt
        self.last_context = context
        return await super().generate(prompt, context, system_instruction)


def test_regression_clean_rag_input():
    """
    Regression Test 1: Clean RAG input.
    Verify RAG receives strictly the original user query without planner prompts.
    """
    async def _run():
        rag_spy = TrackingRAGAgent()
        llm_spy = TrackingLLMAgent()
        from planner.orchestrator import Orchestrator
        from planner.planner_service import PlannerService

        orchestrator = Orchestrator(rag_agent=rag_spy, llm_agent=llm_spy)
        service = ChatService(planner_service=PlannerService(), orchestrator=orchestrator)

        request = ChatRequest(message="What is the main topic of the uploaded document?", conversation_id="reg-001")
        response = await service.process_chat(request)

        assert rag_spy.call_count == 1
        assert rag_spy.last_query == "What is the main topic of the uploaded document?"
        assert "User query:" not in rag_spy.last_query
        assert "Generate the execution plan JSON:" not in rag_spy.last_query

    asyncio.run(_run())


def test_regression_clean_web_search_input():
    """
    Regression Test 2: Clean Web Search input.
    Verify Web Search receives strictly the original user query without planner prompts.
    """
    async def _run():
        web_spy = TrackingWebSearchAgent()
        llm_spy = TrackingLLMAgent()
        from planner.orchestrator import Orchestrator
        from planner.planner_service import PlannerService

        orchestrator = Orchestrator(web_search_agent=web_spy, llm_agent=llm_spy)
        service = ChatService(planner_service=PlannerService(), orchestrator=orchestrator)

        request = ChatRequest(message="What are the latest developments in AI?", conversation_id="reg-002")
        response = await service.process_chat(request)

        assert web_spy.call_count == 1
        assert web_spy.last_query == "What are the latest developments in AI?"
        assert "User query:" not in web_spy.last_query
        assert "Generate the execution plan JSON:" not in web_spy.last_query

    asyncio.run(_run())


def test_regression_clarification_no_tools_called():
    """
    Regression Test 3: Clarification.
    Verify that when action=clarification, RAG, LLM, and Web Search are NOT called,
    and a clear clarification request is returned.
    """
    async def _run():
        rag_spy = TrackingRAGAgent()
        web_spy = TrackingWebSearchAgent()
        llm_spy = TrackingLLMAgent()
        from planner.orchestrator import Orchestrator
        from planner.planner_service import PlannerService

        orchestrator = Orchestrator(rag_agent=rag_spy, llm_agent=llm_spy, web_search_agent=web_spy)
        planner = PlannerService()
        service = ChatService(planner_service=planner, orchestrator=orchestrator)

        # Verify PlannerResult action
        decision = await planner.plan("Tell me more.", conversation_id="reg-003")
        assert decision.action == "clarification"
        assert decision.requires_retrieval is False
        assert decision.requires_generation is False

        # Verify Orchestrator execution
        request = ChatRequest(message="Tell me more.", conversation_id="reg-003")
        response = await service.process_chat(request)

        assert rag_spy.call_count == 0
        assert llm_spy.call_count == 0
        assert web_spy.call_count == 0
        assert response.answer == "Could you clarify what you would like me to explain further?"
        assert response.sources == []

    asyncio.run(_run())


def test_regression_query_aware_llm():
    """
    Regression Test 4: Query-aware LLM.
    Verify 'What is Python?' returns a Python-specific response and not generic AI text.
    """
    async def _run():
        service = ChatService()
        request = ChatRequest(message="What is Python?", conversation_id="reg-004")
        response = await service.process_chat(request)

        assert "python" in response.answer.lower()
        assert "programming language" in response.answer.lower()
        assert "artificial intelligence is a field of computer science" not in response.answer.lower()

    asyncio.run(_run())


def test_regression_context_propagation():
    """
    Regression Test 5: Context propagation.
    Verify RAG chunks are passed to the LLM agent as context for synthesis.
    """
    async def _run():
        rag_spy = TrackingRAGAgent()
        llm_spy = TrackingLLMAgent()
        from planner.orchestrator import Orchestrator
        from planner.planner_service import PlannerService

        orchestrator = Orchestrator(rag_agent=rag_spy, llm_agent=llm_spy)
        service = ChatService(planner_service=PlannerService(), orchestrator=orchestrator)

        request = ChatRequest(message="What security mechanisms are mentioned in the uploaded PDF?", conversation_id="reg-005")
        response = await service.process_chat(request)

        assert llm_spy.call_count == 1
        assert llm_spy.last_prompt == "What security mechanisms are mentioned in the uploaded PDF?"
        assert llm_spy.last_context is not None
        assert len(llm_spy.last_context) > 0
        assert any("zero-trust" in c.lower() for c in llm_spy.last_context)

    asyncio.run(_run())


def test_regression_source_propagation():
    """
    Regression Test 6: Source propagation.
    Verify sources appear in ChatResponse without duplicates.
    """
    async def _run():
        service = ChatService()
        request = ChatRequest(message="What security mechanisms are mentioned in the uploaded PDF?", conversation_id="reg-006")
        response = await service.process_chat(request, document_ids=["sec_spec.pdf"])

        assert len(response.sources) == 2
        documents = [s.document for s in response.sources]
        assert all(d == "sec_spec.pdf" for d in documents)
        pages = [s.page for s in response.sources]
        assert len(pages) == len(set(pages)), "Sources must not contain duplicate pages for the same doc"

    asyncio.run(_run())


# ==============================================================================
# SIH PS 26117 AGENTIC WORKBENCH END-TO-END TEST CASES
# ==============================================================================

def test_sih_case_1_simple_document_question_rag_agent():
    """
    Test Case 1: Simple document question -> RAG Agent.
    Interacts strictly via search_documents(query, user_role, top_k).
    """
    async def _run():
        service = ChatService()
        request = ChatRequest(
            message="What is the zero-trust policy in the uploaded document?",
            conversation_id="sih-int-001",
            user_role="engineer"
        )
        response: ChatResponse = await service.process_chat(request, document_ids=["security.pdf"])

        assert response.status == "success"
        assert len(response.sources) > 0
        assert len(response.evidence) > 0
        assert any(e.source_type == "document" for e in response.evidence)
        assert response.confidence >= 0.8
        assert "zero-trust" in response.answer.lower()

    asyncio.run(_run())


def test_sih_case_2_image_question_vision_agent():
    """
    Test Case 2: Image / P&ID Diagram Question -> Vision Agent.
    Analyzes visual diagrams through clean VisionAgent interface.
    """
    async def _run():
        service = ChatService()
        request = ChatRequest(
            message="What pump and valve configuration is shown on the P&ID diagram?",
            conversation_id="sih-int-002"
        )
        response: ChatResponse = await service.process_chat(request)

        assert response.status == "success"
        assert len(response.evidence) > 0
        assert "p-101" in response.answer.lower()
        assert "valve" in response.answer.lower()

    asyncio.run(_run())


def test_sih_case_3_maintenance_question_rag_plus_analytics():
    """
    Test Case 3: Maintenance question -> RAG + Analytics Agent.
    Combines maintenance manuals with real-time telemetry analytics.
    """
    async def _run():
        service = ChatService()
        request = ChatRequest(
            message="What is the maintenance status and telemetry for pump P-101?",
            conversation_id="sih-int-003"
        )
        response: ChatResponse = await service.process_chat(request)

        assert response.status == "success"
        assert len(response.evidence) >= 2
        source_types = {e.source_type for e in response.evidence}
        assert "document" in source_types
        assert "analytics" in source_types
        assert "vibration" in response.answer.lower() or "telemetry" in response.answer.lower()

    asyncio.run(_run())


def test_sih_case_4_complex_incident_question_multistep_plan():
    """
    Test Case 4: Complex incident question -> Multi-step Plan.
    Decomposes: Incident Log -> Maintenance History -> Equipment Manual -> Telemetry Analytics -> Evidence Verification -> LLM Synthesis.
    """
    async def _run():
        service = ChatService()
        query = "Investigate why Pump P-101 failed and tell me what maintenance action is required."
        request = ChatRequest(message=query, conversation_id="sih-int-004")
        response: ChatResponse = await service.process_chat(request)

        assert response.status == "success"
        assert response.plan is not None
        assert response.plan.intent == "incident_investigation"
        assert len(response.plan.steps) == 6
        
        # Verify step tools
        step_tools = [s.tool for s in response.plan.steps]
        assert step_tools == ["rag", "rag", "rag", "analytics", "verify", "llm"]
        
        # Verify evidence collection
        assert len(response.evidence) >= 4
        assert response.confidence >= 0.85
        assert "root-cause" in response.answer.lower() or "vibration" in response.answer.lower()
        assert "seal" in response.answer.lower()

    asyncio.run(_run())


def test_sih_case_5_unsupported_ambiguous_question_safe_response():
    """
    Test Case 5: Unsupported / Ambiguous Question -> Safe Clarification.
    Fails safely without crashing backend.
    """
    async def _run():
        service = ChatService()
        request = ChatRequest(message="Tell me more.", conversation_id="sih-int-005")
        response: ChatResponse = await service.process_chat(request)

        assert response.status == "clarification"
        assert "clarify" in response.answer.lower()
        assert len(response.sources) == 0

    asyncio.run(_run())


def test_sih_case_6_no_evidence_hallucination_guard():
    """
    Test Case 6: No Evidence Found -> Hallucination Guard.
    Returns explicit uncertainty state ('insufficient_evidence') without hallucinating.
    """
    async def _run():
        service = ChatService()
        request = ChatRequest(
            message="What are the operating limits of nonexistent_equipment_xyz?",
            conversation_id="sih-int-006"
        )
        response: ChatResponse = await service.process_chat(request)

        assert response.status == "insufficient_evidence"
        assert response.confidence == 0.0
        assert len(response.evidence) == 0
        assert "no matching evidence" in (response.reason or "").lower() or "insufficient" in response.answer.lower()

    asyncio.run(_run())


