"""
Interactive CLI demonstration of the Sovereign AI Workbench Planner & Orchestrator.
Run: python demo.py
"""

import asyncio
import json
from planner import (
    PlannerService,
    Orchestrator,
    ChatService,
    ChatRequest,
    MockRAGAgent,
    MockLLMAgent
)


async def main():
    print("=" * 70)
    print("  SOVEREIGN AI WORKBENCH - AI PLANNER & ORCHESTRATOR DEMO")
    print("=" * 70)

    planner = PlannerService()
    chat_service = ChatService()

    sample_queries = [
        ("1. General Question", "What is Python?"),
        ("2. Text / Document QA", "What is the main topic of the uploaded document?"),
        ("3. Image / P&ID Diagram Question", "What pump and valve configuration is shown on the P&ID diagram?"),
        ("4. Multimodal Question", "Compare the valve specifications in the PDF with the P&ID diagram drawing."),
        ("5. Calculation / Reasoning", "Calculate the pressure drop across the pipe with flow rate 50 m3/h."),
        ("6. Ambiguous Query", "Tell me more."),
        ("7. Real-time Web Information", "What are the latest developments in AI?")
    ]


    for label, query in sample_queries:
        print(f"\n{'=' * 70}")
        print(f">>> [{label}] Query: \"{query}\"")
        print(f"{'=' * 70}")

        # 1. Direct Planner Contract
        decision = await planner.plan(query=query, conversation_id="demo-conv-001")
        print("\n--- [PLANNER DECISION CONTRACT (PlannerResult)] ---")
        print(json.dumps(decision.model_dump(exclude_none=True), indent=2))

        # 2. Complete Chat Orchestration
        request = ChatRequest(message=query, conversation_id="demo-conv-001")
        response = await chat_service.process_chat(request, document_ids=["sovereign_spec.pdf"])

        print("\n--- [BACKEND CHAT RESPONSE (ChatResponse)] ---")
        print(f"Answer:  {response.answer}")
        print(f"Sources: {[s.model_dump() for s in response.sources]}")
        print(f"Conv ID: {response.conversation_id}")

    print("\n" + "=" * 70)
    print("[SUCCESS] All sample query plans and orchestration flows completed cleanly!")
    print("=" * 70)



if __name__ == "__main__":
    asyncio.run(main())
