# Sovereign AI Workbench — Backend, RAG & Analytics Integration Guide (SIH PS 26117)

**Problem Statement:** "Sovereign On-Premise Agentic AI Workbench using Open-Weight Multimodal LLMs for Confidential Industrial Work."

This document serves as the formal architectural specification and integration contract between the **AI Planner / Orchestrator** and the other subsystem owners:
* **Backend Team (FastAPI / Chat API)**
* **RAG Team (Document Ingestion & Vector Retrieval)**
* **Vision / Multimodal Team (P&ID & Engineering Diagram Analysis)**
* **Data Analytics Team (Telemetry & Predictive Maintenance)**

---

## 1. High-Level Planner Architecture

The Planner is a lightweight, on-premise agentic coordinator. It decomposes complex industrial engineering queries into discrete tool execution steps, enforces evidence verification, and prevents hallucinations.

```text
                                 User Query
                                     ↓
                            [FastAPI Backend]
                                     ↓
                          [PlannerService.plan()]
                                     ↓
                        Classify Industrial Intent
  ┌──────────────────────────────────┬──────────────────────────────────┐
  │                                  │                                  │
[Incident / Maintenance]      [Vision / P&ID]                    [Document QA]
  │                                  │                                  │
  ├→ RAG (Incident Log)              └→ VisionAgent (analyze_image)     └→ RAGAgent (search_documents)
  ├→ RAG (Maintenance History)
  ├→ RAG (Equipment Manual)
  ├→ Analytics (Telemetry/Sensors)
  │
  └──────────────────────────────────┬──────────────────────────────────┘
                                     ↓
                      [Evidence Verification Agent]
                   (Grounding Check / Hallucination Guard)
                      ├── Sufficient   → [LLM Synthesis] → Success Response
                      └── Insufficient → Return Explicit Uncertainty State
```

---

## 2. Core Tool Interfaces

The Planner calls other subsystems through decoupled abstract interfaces in `planner/interfaces.py`.

### 2.1 RAG / Document Agent Interface
Owned by: **RAG Team**

```python
class BaseRAGAgent(ABC):
    @abstractmethod
    async def search_documents(
        self,
        query: str,
        user_role: Optional[str] = None,
        top_k: int = 5,
        document_ids: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> RAGResult:
        """Searches document store and returns relevant chunks with citations."""
        pass
```

* **Contract Guarantee:** The Planner passes only clean, sanitized queries without prompt leakage.
* **Access Control:** `user_role` is passed directly for on-premise role-based access control.

---

### 2.2 Vision / Multimodal Agent Interface
Owned by: **Vision / Multimodal Team**

```python
class BaseVisionAgent(ABC):
    @abstractmethod
    async def analyze_image(
        self,
        query: str,
        image_path: Optional[str] = None,
        image_data: Optional[Any] = None
    ) -> Dict[str, Any]:
        """Analyzes P&ID diagrams, flowsheets, blueprints, or document page images."""
        pass
```

Expected Return Format:
```json
{
  "image_id": "pid_drawing_01.svg",
  "detected_components": [
    {"tag": "P-101A", "type": "Centrifugal Pump", "status": "In-Service"},
    {"tag": "CV-201", "type": "Check Valve", "line": "4-inch discharge"}
  ],
  "description": "Centrifugal pump P-101A shown with check valve CV-201 on 4-inch discharge.",
  "confidence": 0.95
}
```

---

### 2.3 Analytics / Maintenance Agent Interface
Owned by: **Data Analytics Team**

```python
class BaseAnalyticsAgent(ABC):
    @abstractmethod
    async def get_maintenance_analytics(
        self,
        equipment_id: Optional[str] = None,
        query: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Retrieves sensor telemetry, anomaly detections, and maintenance metrics."""
        pass
```

Expected Return Format:
```json
{
  "equipment_id": "P-101",
  "telemetry_available": true,
  "vibration_rms_mm_s": 7.8,
  "vibration_threshold_mm_s": 4.5,
  "bearing_temperature_c": 92.4,
  "anomaly_detected": true,
  "health_index": "38% (Critical)",
  "recommended_action": "Emergency overhaul: Replace mechanical seal and thrust bearings.",
  "confidence": 0.96
}
```

---

### 2.4 Evidence Verification Agent (Hallucination Guard)
Owned by: **Planner / Orchestration Module**

```python
class BaseEvidenceVerifier(ABC):
    @abstractmethod
    async def verify_evidence(
        self,
        query: str,
        evidence: List[EvidenceItem],
        answer: Optional[str] = None
    ) -> VerificationResult:
        """Validates factual grounding across collected evidence before final response."""
        pass
```

* If evidence is missing or confidence is below threshold (< 0.3):
  The Orchestrator returns an explicit uncertainty state without hallucinating facts.

---

## 3. Backend Integration Contract (`POST /api/chat`)

### 3.1 Input Contract (`ChatRequest`)

```python
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User query.")
    conversation_id: Optional[str] = Field(default=None, description="Session ID.")
    user_role: Optional[str] = Field(default=None, description="User access role.")
```

### 3.2 Output Contract (`ChatResponse`)

```python
class ChatResponse(BaseModel):
    status: Literal["success", "insufficient_evidence", "error", "clarification"]
    answer: str
    conversation_id: Optional[str] = None
    sources: List[SourceMetadata] = []
    evidence: List[EvidenceItem] = []
    confidence: float = 1.0
    steps: Optional[List[PlanStep]] = None
    plan: Optional[ExecutionPlan] = None
    reason: Optional[str] = None
```

#### Successful Execution Example:
```json
{
  "status": "success",
  "confidence": 0.94,
  "answer": "Pump P-101 failed due to severe mechanical seal blowout caused by high vibration (7.8 mm/s vs 4.5 mm/s limit)...",
  "sources": [
    {"document": "pump_p101_incident_report.pdf", "page": 1, "score": 0.96},
    {"document": "pump_p101_maintenance_history.pdf", "page": 4, "score": 0.94}
  ],
  "evidence": [
    {"source_type": "document", "title": "Incident Log", "confidence": 0.96, "content": "..."},
    {"source_type": "analytics", "title": "Telemetry P-101", "confidence": 0.96, "content": "..."}
  ]
}
```

#### Insufficient Evidence (Hallucination Guard) Example:
```json
{
  "status": "insufficient_evidence",
  "confidence": 0.0,
  "answer": "I cannot answer this question because no relevant documents, telemetry, or diagrams were found in the knowledge repository.",
  "reason": "No matching evidence found in on-premise knowledge repository.",
  "sources": [],
  "evidence": []
}
```

---

## 4. Multi-Step Task Decomposition Example

**User Query:**
> *"Investigate why Pump P-101 failed and tell me what maintenance action is required."*

**Decomposed Execution Plan:**
1. `Step 1 (rag)`: Retrieve Incident Report & Alarm Logs for P-101.
2. `Step 2 (rag)`: Retrieve Maintenance History & Overhaul Records for P-101.
3. `Step 3 (rag)`: Retrieve Technical Manual & Operating Limits for P-101.
4. `Step 4 (analytics)`: Query Telemetry for vibration and bearing temperature anomalies.
5. `Step 5 (verify)`: Verify cross-source grounding and evidence consistency.
6. `Step 6 (llm)`: Synthesize root-cause failure analysis and required maintenance actions.

---

## 5. Verification & Tests

The test suite validates all 6 required capabilities:
1. **Simple Document QA** → `RAGAgent.search_documents`
2. **Image / P&ID QA** → `VisionAgent.analyze_image`
3. **Maintenance Analytics** → RAG + Analytics Agent
4. **Complex Incident Investigation** → 6-step multi-agent plan
5. **Unsupported / Ambiguous Queries** → Safe clarification without crashing
6. **No Evidence Found** → Hallucination guard with `status="insufficient_evidence"`

```bash
pytest -v
python demo.py
```



