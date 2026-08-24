# Sovereign AI Workbench — AI Planner & Orchestration Layer

A modular, production-ready AI Planner and Orchestration engine built for the **Sovereign AI Workbench** SIH hackathon project.

Designed to sit cleanly behind FastAPI (`POST /api/chat`) and coordinate between **RAG Services**, **LLM Services**, and **Web Search Tools** without tight coupling or breaking public API contracts.

---

## 📁 Project Structure

```text
d:/SIH-117/
├── planner/
│   ├── __init__.py            # Clean public API exports
│   ├── schemas.py             # Pydantic models (PlanStep, ExecutionPlan, SourceMetadata, ChatRequest, ChatResponse)
│   ├── prompts.py             # System prompt & structured few-shot instructions
│   ├── interfaces.py          # Abstract interfaces (BaseRAGAgent, BaseLLMAgent, BasePlannerLLMClient)
│   ├── adapters.py            # Out-of-the-box mock adapters & HTTP connectors
│   ├── planner_service.py     # Planner service: query validation, LLM call, robust JSON parser
│   ├── orchestrator.py        # Sequential executor: pipeline context passing & source collection
│   └── chat_service.py        # FastAPI integration bridge
├── tests/
│   ├── __init__.py
│   ├── test_planner.py        # Unit tests covering all 6 query test cases & schema invariants
│   ├── test_orchestrator.py   # Unit tests for step execution, context chaining & source deduplication
│   └── test_integration.py    # Integration tests for ChatService POST /api/chat contract
├── demo.py                    # Interactive CLI demonstration
├── requirements.txt           # Minimal dependencies (pydantic>=2.0, pytest, pytest-asyncio)
├── INTEGRATION_GUIDE.md       # Team contract guide for RAG & Backend engineers
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

### 3. Run Automated Test Suite
```bash
python -m pytest -v
```

---

## 🎯 Verification Matrix

| Test Case | Query | Expected Routing | Status |
| :--- | :--- | :--- | :--- |
| **Test 1 — General Question** | `"What is artificial intelligence?"` | `LLM` (`requires_rag=False`) | ✅ Passed |
| **Test 2 — Document Question** | `"What security mechanisms are mentioned in the uploaded PDF?"` | `RAG -> LLM` (`requires_rag=True`) | ✅ Passed |
| **Test 3 — Document Summarization** | `"Summarize the uploaded document."` | `RAG -> LLM` (`requires_rag=True`) | ✅ Passed |
| **Test 4 — Document Comparison** | `"Compare the two architectures described in the uploaded document."` | `RAG -> LLM` (`requires_rag=True`) | ✅ Passed |
| **Test 5 — Current Information** | `"What are the latest developments in AI?"` | `WEB_SEARCH -> LLM` | ✅ Passed |
| **Test 6 — Empty Query** | `""` or `"   "` | Raises `PlannerValidationError` | ✅ Passed |
| **Code Fence Sanitizer** | Markdown-wrapped ` ```json ` | Extracts & validates clean JSON | ✅ Passed |
| **Tool Guardrails** | Unsupported tools | Rejects invalid tool names | ✅ Passed |
| **Source Citation Flow** | Multi-chunk retrieval | Preserves `document` and `page` | ✅ Passed |
