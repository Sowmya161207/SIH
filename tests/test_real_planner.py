import asyncio

from planner.planner_service import PlannerService
from planner.orchestrator import Orchestrator
from planner.real_adapters import (
    RealAnalyticsAgent,
    RealRAGAgent,
    RealLLMAgent,
)


async def main():
    query = "Is Pump P-101 showing abnormal vibration?"

    print("\n=== 1. PLANNER ===")

    planner = PlannerService()
    plan = await planner.create_plan(query)

    print("Intent:", plan.intent)
    print("Requires RAG:", plan.requires_rag)

    for step in plan.steps:
        print(
            f"Step {step.step}: "
            f"tool={step.tool}, action={step.action}"
        )

    print("\n=== 2. ORCHESTRATOR ===")

    orchestrator = Orchestrator(
        rag_agent=RealRAGAgent(),
        analytics_agent=RealAnalyticsAgent(),
        llm_agent=RealLLMAgent(),
    )

    response = await orchestrator.execute_plan(
        plan=plan,
        original_query=query,
    )

    print("Status:", response.status)
    print("Answer:", response.answer)
    print("Confidence:", response.confidence)
    print("Evidence count:", len(response.evidence))

    print("\n=== 3. SOURCES ===")

for source in response.sources:
    print(source)

print("\n=== 4. EVIDENCE ===")

for evidence in response.evidence:
    print("Type:", evidence.source_type)
    print("Title:", evidence.title)
    print("Confidence:", evidence.confidence)
    print("Content:", evidence.content)


if __name__ == "__main__":
    asyncio.run(main())