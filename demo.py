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
        ("1. Simple Document QA", "What is the zero-trust policy in the uploaded document?"),
        ("2. Image / P&ID Diagram", "What pump and valve configuration is shown on the P&ID diagram?"),
        ("3. Maintenance + Analytics", "What is the maintenance status and telemetry for pump P-101?"),
        ("4. Complex Incident Investigation", "Investigate why Pump P-101 failed and tell me what maintenance action is required."),
        ("5. Unsupported / Ambiguous Query", "Tell me more."),
        ("6. No Evidence / Hallucination Guard", "What are the operating limits of nonexistent_equipment_xyz?"),
        ("7. General Question", "What is Python?")
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
        response = await chat_service.process_chat(request, document_ids=["sovereign_spec.pdf"])

        print("\n--- [BACKEND CHAT RESPONSE (ChatResponse)] ---")
        print(f"Status:     {response.status}")
        print(f"Confidence: {response.confidence}")
        print(f"Evidence:   {len(response.evidence)} item(s) verified")
        print(f"Answer:     {response.answer}")
        if response.sources:
            print(f"Sources:    {[s.model_dump() for s in response.sources]}")
        if response.reason:
            print(f"Reason:     {response.reason}")


    print("\n" + "=" * 70)
    print("[SUCCESS] All sample query plans and orchestration flows completed cleanly!")
    print("=" * 70)



if __name__ == "__main__":
    asyncio.run(main())
