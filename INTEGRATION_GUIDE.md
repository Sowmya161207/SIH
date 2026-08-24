# Sovereign AI Workbench — Backend & Team Integration Guide

This guide specifies how the **Backend** (`ChatService` / FastAPI) calls the **AI Planner** to determine what action should happen next for any user query.

---

## 1. Direct Planner Contract: `PlannerService.plan()`

The Backend invokes `PlannerService.plan(...)` to obtain a structured `PlannerResult` decision:

```text
User Query
    ↓
Backend (ChatService)
    ↓
PlannerService.plan(query, conversation_id)
    ↓
PlannerResult { action, query, requires_retrieval, requires_generation, ... }
    ↓
[RAG / Direct LLM / Clarification]
```

### 1.1 Planner Input Contract

```python
result = await planner.plan(
    query="What is the main topic of the uploaded document?",
    conversation_id="test-001"  # Optional
)
```

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `query` | `str` | Yes | The user's prompt or question. |
| `conversation_id` | `Optional[str]` | No | Optional conversation/session identifier. |

---

### 1.2 Planner Output Contract (`PlannerResult`)

```python
class PlannerResult(BaseModel):
    action: Literal["rag", "direct_llm", "clarification", "web_search"]
    query: str
    requires_retrieval: bool
    requires_generation: bool
    conversation_id: Optional[str] = None
    reason: Optional[str] = None
    steps: Optional[List[PlanStep]] = None
```

| Field | Type | Description |
| :--- | :--- | :--- |
| `action` | `str` | One of: `"rag"`, `"direct_llm"`, `"clarification"`, `"web_search"` |
| `query` | `str` | The sanitized user query |
| `requires_retrieval` | `bool` | `True` if document retrieval via RAG is needed |
| `requires_generation` | `bool` | `True` if LLM answer synthesis is needed |
| `conversation_id` | `Optional[str]` | The passed conversation ID |
| `reason` | `Optional[str]` | High-level rationale/intent for debugging |
| `steps` | `Optional[List[PlanStep]]` | Granular sequential execution steps |

---

## 2. Example Decisions

### Document-Related Question
**Input:**
```text
"What is the main topic of the uploaded document?"
```
**Output:**
```json
{
  "action": "rag",
  "query": "What is the main topic of the uploaded document?",
  "requires_retrieval": true,
  "requires_generation": true,
  "conversation_id": "test-001",
  "reason": "Plan generated for intent: 'document_qa'"
}
```

---

### General Question
**Input:**
```text
"What is Python?"
```
**Output:**
```json
{
  "action": "direct_llm",
  "query": "What is Python?",
  "requires_retrieval": false,
  "requires_generation": true,
  "conversation_id": "test-001",
  "reason": "Plan generated for intent: 'general_qa'"
}
```

---

### Ambiguous Question
**Input:**
```text
"Tell me more."
```
**Output:**
```json
{
  "action": "clarification",
  "query": "Tell me more.",
  "requires_retrieval": false,
  "requires_generation": false,
  "conversation_id": "test-001",
  "reason": "Query is ambiguous or underspecified; requires clarification before execution."
}
```

---

## 3. Drop-In Backend Invocation (`ChatService`)

Here is how the Backend owner can integrate `PlannerService` into `ChatService`:

```python
"""
backend/app/services/chat_service.py
"""
from planner import PlannerService, PlannerResult

planner = PlannerService()


class ChatService:
    @staticmethod
    async def handle_message(query: str, conversation_id: str | None = None):
        # 1. Ask the AI Planner what to do next
        plan: PlannerResult = await planner.plan(
            query=query,
            conversation_id=conversation_id
        )

        # 2. Branch deterministically based on structured plan
        if plan.action == "clarification":
            return {
                "answer": "Could you please clarify your question or specify which document you are referring to?",
                "conversation_id": conversation_id,
                "sources": []
            }

        elif plan.action == "rag" and plan.requires_retrieval:
            # Call RAG retrieval -> LLM generation
            # rag_result = await rag_service.retrieve(plan.query)
            # answer = await llm_service.generate(plan.query, context=rag_result.chunks)
            ...

        elif plan.action == "direct_llm":
            # Direct LLM generation without RAG
            # answer = await llm_service.generate(plan.query)
            ...
```

---

## 4. Error Behavior

- **Empty / Whitespace Input:** Returns `action="clarification"` with `requires_retrieval=False`, `requires_generation=False`, and a clear explanation in `reason`.
- **Ambiguous / Underspecified Input:** Returns `action="clarification"`.
- **Parsing / Network Errors:** Returns structured `PlannerResult` with `action="clarification"` and details in `reason`, ensuring the backend **never crashes** or receives untyped random text.

---

## 5. Dependencies & Environment Variables

### Dependencies (`requirements.txt`)
```text
pydantic>=2.0.0
pytest>=8.0.0
pytest-asyncio>=0.23.0
```

### Environment Variables
| Variable | Values | Default | Purpose |
| :--- | :--- | :--- | :--- |
| `PLANNER_MODE` | `mock`, `llm` | `mock` | Seamless offline/mock execution so Backend testing is never blocked. |

---

## 6. Verification & Tests

Run all unit tests verifying RAG, Direct LLM, Clarification, and multi-step plans:

```bash
pytest
```

