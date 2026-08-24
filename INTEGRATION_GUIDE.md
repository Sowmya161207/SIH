# Sovereign AI Workbench — Backend & Team Integration Guide (SIH PS 26117)

This guide specifies how the **Backend** (`ChatService` / FastAPI) calls the **AI Planner** to classify tasks, determine modality requirements (Text / Image / P&ID / Multimodal / Reasoning), and route to open-weight models.

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
PlannerResult { action, task_type, requires_text, requires_image, retrieval_required, selected_model, ... }
    ↓
[RAG / Direct LLM / Vision / Multimodal / Calculation]
```

### 1.1 Planner Input Contract

```python
result = await planner.plan(
    query="Compare the valve specifications in the PDF with the P&ID diagram drawing.",
    conversation_id="test-001"  # Optional
)
```

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `query` | `str` | Yes | The user's prompt, document question, or diagram query. |
| `conversation_id` | `Optional[str]` | No | Optional conversation/session identifier. |

---

### 1.2 Planner Output Contract (`PlannerResult`)

```python
class PlannerResult(BaseModel):
    action: Literal["rag", "direct_llm", "clarification", "web_search"]
    task_type: Literal[
        "document_qa",
        "document_summarization",
        "document_comparison",
        "image_qa",
        "multimodal_qa",
        "calculation_reasoning",
        "web_search_qa",
        "general_qa",
        "clarification"
    ]
    query: str
    requires_retrieval: bool
    retrieval_required: bool
    requires_generation: bool
    requires_text: bool
    requires_image: bool
    capability: Optional[str] = "text"
    selected_model: Optional[str] = None
    conversation_id: Optional[str] = None
    reason: Optional[str] = None
    steps: Optional[List[PlanStep]] = None
```

| Field | Type | Description |
| :--- | :--- | :--- |
| `action` | `str` | One of: `"rag"`, `"direct_llm"`, `"clarification"`, `"web_search"` |
| `task_type` | `str` | Classified task (e.g. `"document_qa"`, `"image_qa"`, `"multimodal_qa"`, `"calculation_reasoning"`) |
| `query` | `str` | The sanitized user query |
| `requires_retrieval` / `retrieval_required` | `bool` | `True` if document or diagram retrieval is needed |
| `requires_generation` | `bool` | `True` if answer synthesis is needed |
| `requires_text` | `bool` | `True` if textual processing is involved |
| `requires_image` | `bool` | `True` if visual diagram / P&ID processing is involved |
| `capability` | `str` | Category: `"text"`, `"vision"`, `"multimodal"`, `"reasoning"` |
| `selected_model` | `str` | Configured open-weight model (e.g. `llama3:8b`, `llava:7b`, `qwen-vl:7b`, `qwen2.5-coder:7b`) |
| `conversation_id` | `Optional[str]` | The passed conversation ID |
| `reason` | `Optional[str]` | High-level rationale/intent for debugging |

---

## 2. Example Decisions for Key Capabilities

### 2.1 Image / P&ID Diagram Question
**Input:** `"What pump and valve configuration is shown on the P&ID diagram?"`
**Output:**
```json
{
  "action": "rag",
  "task_type": "image_qa",
  "query": "What pump and valve configuration is shown on the P&ID diagram?",
  "requires_retrieval": true,
  "requires_generation": true,
  "requires_text": false,
  "requires_image": true,
  "retrieval_required": true,
  "capability": "vision",
  "selected_model": "llava:7b"
}
```

---

### 2.2 Multimodal Question (Text Specs + Diagram/P&ID)
**Input:** `"Compare the valve specifications in the PDF with the P&ID diagram drawing."`
**Output:**
```json
{
  "action": "rag",
  "task_type": "multimodal_qa",
  "query": "Compare the valve specifications in the PDF with the P&ID diagram drawing.",
  "requires_retrieval": true,
  "requires_generation": true,
  "requires_text": true,
  "requires_image": true,
  "retrieval_required": true,
  "capability": "multimodal",
  "selected_model": "qwen-vl:7b"
}
```

---

### 2.3 Calculation / Quantitative Reasoning
**Input:** `"Calculate the pressure drop across the pipe with flow rate 50 m3/h."`
**Output:**
```json
{
  "action": "direct_llm",
  "task_type": "calculation_reasoning",
  "query": "Calculate the pressure drop across the pipe with flow rate 50 m3/h.",
  "requires_retrieval": false,
  "requires_generation": true,
  "requires_text": true,
  "requires_image": false,
  "retrieval_required": false,
  "capability": "reasoning",
  "selected_model": "qwen2.5-coder:7b"
}
```

---

### 2.4 Document Question
**Input:** `"What is the main topic of the uploaded document?"`
**Output:**
```json
{
  "action": "rag",
  "task_type": "document_qa",
  "query": "What is the main topic of the uploaded document?",
  "requires_retrieval": true,
  "requires_generation": true,
  "requires_text": true,
  "requires_image": false,
  "retrieval_required": true,
  "capability": "text",
  "selected_model": "llama3:8b"
}
```

---

### 2.5 Ambiguous Question
**Input:** `"Tell me more."`
**Output:**
```json
{
  "action": "clarification",
  "task_type": "clarification",
  "query": "Tell me more.",
  "requires_retrieval": false,
  "requires_generation": false,
  "requires_text": false,
  "requires_image": false,
  "retrieval_required": false,
  "reason": "Query is ambiguous or underspecified; requires clarification before execution."
}
```

---

## 3. Drop-In Backend Invocation (`ChatService`)

```python
"""
backend/app/services/chat_service.py
"""
from planner import PlannerService, PlannerResult

planner = PlannerService()


class ChatService:
    @staticmethod
    async def handle_message(query: str, conversation_id: str | None = None):
        # 1. Obtain structured capability decision
        plan: PlannerResult = await planner.plan(
            query=query,
            conversation_id=conversation_id
        )

        # 2. Branch deterministically
        if plan.action == "clarification":
            return {
                "answer": "Could you please clarify your question or specify which document/diagram you are referring to?",
                "conversation_id": conversation_id,
                "sources": []
            }

        elif plan.task_type == "multimodal_qa":
            # Delegate to Multimodal Model (e.g. Qwen-VL / LLaVA) with document chunks & image context
            ...

        elif plan.task_type == "image_qa":
            # Delegate to Vision Model with retrieved diagram/P&ID
            ...

        elif plan.task_type == "calculation_reasoning":
            # Delegate to Reasoning Model (e.g. Qwen2.5-Coder)
            ...

        elif plan.action == "rag":
            # Delegate to Text RAG
            ...

        elif plan.action == "direct_llm":
            # Direct text generation
            ...
```

---

## 4. Error Behavior & Safe Failure

- **Empty / Whitespace Input:** Returns `action="clarification"` and `task_type="clarification"`.
- **Parsing / Network Errors:** Returns structured `PlannerResult` with `action="clarification"` and diagnostics in `reason`. The backend **never crashes**.

---

## 5. Configurable Open-Weight Model Registry

Configure models via environment variables without hardcoding providers:

| Environment Variable | Default Model | Capability Tier |
| :--- | :--- | :--- |
| `TEXT_MODEL` | `llama3:8b` | Text & Document QA |
| `VISION_MODEL` | `llava:7b` | P&ID & Engineering Diagram Analysis |
| `MULTIMODAL_MODEL` | `qwen-vl:7b` | Cross-modal (Text + Diagram) QA |
| `REASONING_MODEL` | `qwen2.5-coder:7b` | Mathematical & Calculation Reasoning |
| `ROUTER_MODEL` | `llama3.2:3b` | Fast Intent Classification |
| `PLANNER_MODE` | `mock` | `mock` (offline rule-based) or `llm` |

---

## 6. Verification & Tests

Run all 30 tests covering multimodal routing, calculation reasoning, and safe failure:

```bash
pytest -v
python demo.py
```


