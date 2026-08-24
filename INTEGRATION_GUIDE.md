# Sovereign AI Workbench — Backend, RAG & Analytics Integration Guide (SIH PS 26117)

**Problem Statement:** "Sovereign On-Premise Agentic AI Workbench using Open-Weight Multimodal LLMs for Confidential Industrial Work."

This document serves as the formal architectural specification and integration contract between the **AI Planner / Orchestrator** and the other subsystem owners:
* **Backend Team (FastAPI / Chat API)**
* **RAG Team (Document Ingestion & Vector Retrieval)**
* **Vision / Multimodal Team (P&ID & Engineering Diagram Analysis)**
* **Data Analytics Team (Telemetry & Predictive Maintenance)**

---

## 1. High-Level Planner Architecture & Decision Layer

The AI Planner serves as the intelligence and decision-making layer that routes incoming queries to the appropriate on-premise industrial capability without directly executing internal teammate logic.

```text
                                 User Query
                                     ↓
                               [AI Planner]
                                     ↓
                          Determine Required Tools
  ┌───────────────────┬───────────────────┬───────────────────┬───────────────────┐
  │                   │                   │                   │                   │
 [RAG]           [Analytics]       [Vision/Diagram]     [Direct LLM]        [Multi-Tool]
 (SOP / Manual)  (Telemetry Anomaly) (P&ID Schematic)   (General QA)  (Risk / Root-Cause)
  │                   │                   │                   │                   │
  └───────────────────┴─────────┬─────────┴───────────────────┴───────────────────┘
                                ↓
                 [Evidence Verification Agent]
             (Grounding Check / Hallucination Guard)
                 ├── Sufficient   → [LLM Synthesis] → Success Response
                 └── Insufficient → Return Explicit Uncertainty State
```

---

## 2. Decision Schema (`PlannerResult`)

Every decision produced by the planner conforms to the following Pydantic schema:

```json
{
  "action": "rag",
  "requires_retrieval": true,
  "requires_analytics": false,
  "requires_vision": false,
  "requires_generation": true,
  "query": "What does the Pump P-101 SOP say?",
  "reason": "Question requires information from company documents (SOP/manuals).",
  "task_type": "document_qa",
  "selected_tools": ["rag", "llm"],
  "capability": "text",
  "selected_model": "llama3:8b",
  "conversation_id": "conv-101",
  "user_context": {"user_role": "operator", "workspace_id": "unit_4"},
  "fallback_action": null,
  "steps": [
    {
      "step": 1,
      "tool": "rag",
      "action": "retrieve",
      "input": "What does the Pump P-101 SOP say?"
    },
    {
      "step": 2,
      "tool": "llm",
      "action": "synthesize",
      "input": "Synthesize a grounded answer based strictly on the retrieved document chunks."
    }
  ]
}
```

### Schema Field Definitions:
| Field | Type | Description |
| :--- | :--- | :--- |
| `action` | `Literal["rag", "analytics", "vision", "direct_llm", "multi_tool", "clarification", "web_search"]` | Primary determined action |
| `requires_retrieval` | `bool` | True if document/manual retrieval via RAG is required |
| `requires_analytics` | `bool` | True if sensor telemetry / anomaly analytics is required |
| `requires_vision` | `bool` | True if P&ID diagram / blueprint inspection is required |
| `requires_generation` | `bool` | True if local LLM answer synthesis is required |
| `query` | `str` | Cleaned, normalized user query |
| `reason` | `str` | Explainable decision rationale |
| `task_type` | `str` | Detailed industrial task classification |
| `selected_tools` | `List[str]` | List of tools invoked in this plan (`rag`, `analytics`, `vision`, `verify`, `llm`) |
| `selected_model` | `str` | Configured local open-weight model (e.g. `llama3:8b`, `qwen2.5-coder:7b`, `llava:7b`) |
| `fallback_action` | `Optional[str]` | Fallback route activated if a tool is offline/unavailable |
| `user_context` | `Optional[dict]` | User role and workspace access boundaries |
| `steps` | `List[PlanStep]` | Atomic, ordered execution steps |

---

## 3. Example Queries and Planner Decisions

### Example 1: Document SOP Query
* **Query:** `"What does the Pump P-101 SOP say?"`
* **Route:** `RAG`
```json
{
  "action": "rag",
  "requires_retrieval": true,
  "requires_analytics": false,
  "requires_vision": false,
  "requires_generation": true,
  "query": "What does the Pump P-101 SOP say?",
  "reason": "Question requires information from company documents (SOP/manuals)."
}
```

### Example 2: Real-time Telemetry Query
* **Query:** `"Is Pump P-101 showing abnormal vibration?"`
* **Route:** `Analytics`
```json
{
  "action": "analytics",
  "requires_retrieval": false,
  "requires_analytics": true,
  "requires_vision": false,
  "requires_generation": true,
  "query": "Is Pump P-101 showing abnormal vibration?",
  "reason": "Question requires real-time telemetry sensor analysis for vibration/temperature anomalies."
}
```

### Example 3: Visual Inspection Query
* **Query:** `"What is shown in this P&ID?"`
* **Route:** `Vision`
```json
{
  "action": "vision",
  "requires_retrieval": false,
  "requires_analytics": false,
  "requires_vision": true,
  "requires_generation": true,
  "query": "What is shown in this P&ID?",
  "reason": "Question requires visual analysis of P&ID engineering diagrams and schematics."
}
```

### Example 4: Risk Assessment / Incident Troubleshooting
* **Query:** `"Why is Pump P-101 at risk and what should we do?"`
* **Route:** `Multi-Tool (RAG + Analytics + Verify + LLM)`
```json
{
  "action": "rag",
  "requires_retrieval": true,
  "requires_analytics": true,
  "requires_vision": false,
  "requires_generation": true,
  "query": "Why is Pump P-101 at risk and what should we do?",
  "selected_tools": ["rag", "analytics", "verify", "llm"],
  "reason": "Complex question requiring cross-referencing document procedures with telemetry analytics."
}
```

---

## 4. Backend Integration Instructions

Backend engineers can invoke the planner using either the standalone `plan_query` function or the `PlannerService` class:

### Method 1: Simple Function API (`plan_query`)

```python
from planner import plan_query

# 1. Evaluate a query
decision = await plan_query(
    query="What does the Pump P-101 SOP say?",
    conversation_id="conv-123",
    user_context={"user_role": "operator", "workspace_id": "refinery-alpha"}
)

# 2. Check tool requirements
if decision.requires_retrieval:
    # Trigger RAG pipeline
    pass
if decision.requires_analytics:
    # Trigger Telemetry pipeline
    pass
if decision.requires_vision:
    # Trigger Vision pipeline
    pass
```

### Method 2: Tool Availability & Fallback Behavior

When certain tools are offline or not deployed in an environment, pass `available_tools`:

```python
# Analytics agent is offline
decision = await plan_query(
    query="Is Pump P-101 showing abnormal vibration?",
    available_tools=["rag", "llm"]  # analytics not available
)

print(decision.fallback_action)  # "direct_llm"
print(decision.reason)           # Contains fallback notification
```

### Method 3: Full Chat Service Integration (`POST /api/chat`)

```python
from fastapi import APIRouter
from planner import ChatService, ChatRequest, ChatResponse

router = APIRouter()
chat_service = ChatService()

@router.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    return await chat_service.process_chat(request)
```

---

## 5. Security & On-Premise Governance

* **Zero Cloud AI Services:** All planner routing uses local open-weight model IDs (`llama3:8b`, `qwen2.5-coder:7b`, `llava:7b`).
* **Context Preservation & RBAC:** `user_context` (user role, allowed document scopes) is strictly passed through all decisions.
* **Hallucination Guard:** Responses return `status="insufficient_evidence"` when required grounding data is missing.

---

## 6. Test Commands

```bash
# Run all 42 unit, contract, and regression tests
pytest -v

# Run the interactive CLI demonstration
python demo.py
```




