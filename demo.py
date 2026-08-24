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
        ("1. Document SOP (RAG)", "What does the Pump P-101 SOP say?"),
        ("2. Real-time Telemetry (Analytics)", "Is Pump P-101 showing abnormal vibration?"),
        ("3. Visual Diagram Inspection (Vision)", "What is shown in this P&ID?"),
        ("4. Risk Assessment (Multi-Tool RAG + Analytics)", "Why is Pump P-101 at risk and what should we do?"),
        ("5. Ambiguous Query (Clarification)", "Tell me more."),
        ("6. Hallucination Guard (No Evidence)", "What are the operating limits of nonexistent_equipment_xyz?"),
        ("7. General Knowledge (Direct Local LLM)", "What is Python?")
    ]

    for label, query in sample_queries:
        print(f"\n{'=' * 75}")
        print(f">>> [{label}] Query: \"{query}\"")
        print(f"{'=' * 75}")

        # 1. Direct Planner Contract
        decision = await planner.plan(query=query, conversation_id="sih-demo-001")
        print("\n--- [PLANNER DECISION CONTRACT (PlannerResult)] ---")
        print(json.dumps(decision.model_dump(exclude_none=True), indent=2))

        # 2. Complete Chat Orchestration
        request = ChatRequest(message=query, conversation_id="sih-demo-001")
        response = await chat_service.process_chat(request, document_ids=["pump_p101_sop.pdf"])

        print("\n--- [BACKEND CHAT RESPONSE (ChatResponse)] ---")
        print(f"Status:     {response.status}")
        print(f"Confidence: {response.confidence}")
        print(f"Evidence:   {len(response.evidence)} item(s) verified")
        print(f"Answer:     {response.answer}")
        if response.sources:
            print(f"Sources:    {[s.model_dump() for s in response.sources]}")
        if response.reason:
            print(f"Reason:     {response.reason}")

    # 3. Tool Unavailable Fallback Demo
    print(f"\n{'=' * 75}")
    print(">>> [8. Fallback Demo] Query: 'Is Pump P-101 showing abnormal vibration?' with Analytics Tool Offline")
    print(f"{'=' * 75}")
    fallback_decision = await planner.plan(
        query="Is Pump P-101 showing abnormal vibration?",
        available_tools=["rag", "llm"]  # analytics offline
    )
    print("\n--- [FALLBACK PLANNER DECISION] ---")
    print(json.dumps(fallback_decision.model_dump(exclude_none=True), indent=2))


    print("\n" + "=" * 70)
    print("[SUCCESS] All sample query plans and orchestration flows completed cleanly!")
    print("=" * 70)



if __name__ == "__main__":
    asyncio.run(main())
