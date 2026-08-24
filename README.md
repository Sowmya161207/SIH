# Sovereign AI Workbench — AI Planner & Orchestration Layer (SIH 26117)

A modular, on-premise AI Planner and Decision-Making Layer built for the **Sovereign AI Workbench** (SIH Problem Statement 26117: Confidential Industrial Work using Open-Weight Multimodal LLMs).

Determines which tool/capability should handle incoming user requests without directly executing teammate internal implementations or calling external cloud AI services.

---

## 📁 Project Structure

```text
d:/SIH-117/
├── planner/
│   ├── __init__.py            # Clean public API exports (plan_query, PlannerService, Orchestrator, ChatService)
│   ├── schemas.py             # Pydantic decision contracts (PlannerResult, ExecutionPlan, PlanStep, ChatRequest, ChatResponse)
│   ├── prompts.py             # Industrial planner system prompt & structured JSON few-shot instructions
│   ├── interfaces.py          # Abstract interfaces (BaseRAGAgent, BaseVisionAgent, BaseAnalyticsAgent, BaseEvidenceVerifier, BaseLLMAgent)
│   ├── adapters.py            # Deterministic mock adapters, rule engine, & HTTP connectors
│   ├── planner_service.py     # Planner service: query classification, tool selection, fallback handling, plan_query API
│   ├── orchestrator.py        # Multi-agent orchestrator: evidence aggregation & hallucination guard
│   └── chat_service.py        # FastAPI integration bridge
├── tests/
│   ├── __init__.py
│   ├── test_planner.py        # Unit tests covering decision contracts, 4 industrial examples, tool fallback, security context
│   ├── test_orchestrator.py   # Unit tests for step execution, context chaining & source deduplication
│   └── test_integration.py    # End-to-end integration tests for POST /api/chat contract & regression suite
├── demo.py                    # Interactive CLI demonstration
├── requirements.txt           # Minimal dependencies (pydantic>=2.0, pytest, pytest-asyncio)
├── INTEGRATION_GUIDE.md       # Complete integration guide for Backend, RAG, Vision, and Analytics engineers
└── README.md
```

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Interactive Demo
```bash
python demo.py
```

### 3. Run Automated Test Suite (42 Tests)
```bash
pytest -v
```

---

## 🎯 Verification & Routing Matrix

| Test Category | Query Example | Selected Tool(s) | Action / Capability | Status |
| :--- | :--- | :--- | :--- | :--- |
| **1. Document SOP** | `"What does the Pump P-101 SOP say?"` | `RAG` + `LLM` | `action="rag"`, `requires_retrieval=True` | ✅ Passed |
| **2. Telemetry Anomaly** | `"Is Pump P-101 showing abnormal vibration?"` | `Analytics` + `LLM` | `action="analytics"`, `requires_analytics=True` | ✅ Passed |
| **3. P&ID Blueprint** | `"What is shown in this P&ID?"` | `Vision` + `LLM` | `action="vision"`, `requires_vision=True` | ✅ Passed |
| **4. Multi-Tool Risk** | `"Why is Pump P-101 at risk and what should we do?"` | `RAG` + `Analytics` + `Verify` + `LLM` | `action="rag"`, Multi-Tool | ✅ Passed |
| **5. Incident Investigation** | `"Investigate why Pump P-101 failed and what maintenance is required"` | `RAG` (x3) + `Analytics` + `Verify` + `LLM` | 6-Step Multi-Agent Plan | ✅ Passed |
| **6. Ambiguous / Short** | `"Tell me more."` | None (Direct Clarification) | `action="clarification"` | ✅ Passed |
| **7. Hallucination Guard** | `"What are the operating limits of nonexistent_xyz?"` | Evidence Verifier Guard | `status="insufficient_evidence"` | ✅ Passed |
| **8. General Knowledge** | `"What is Python?"` | Local `LLM` | `action="direct_llm"` | ✅ Passed |
| **9. Tool Fallback** | Analytics offline | `fallback_action="direct_llm"` | Graceful Degradation | ✅ Passed |
| **10. Security Context** | RBAC `user_context` preservation | Enforces workspace boundary | Zero Cloud AI calls | ✅ Passed |
