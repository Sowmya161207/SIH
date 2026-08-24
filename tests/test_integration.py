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

