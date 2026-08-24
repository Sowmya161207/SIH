# Sovereign On-Premise Deployment, Security & Data-Leakage Firewall Guide

**Project:** Sovereign On-Premise Agentic AI Workbench for MRPL (SIH26117)  
**Role:** Sovereign Deployment, Security & Data-Leakage Firewall Engineer (`Yoagesh`)  
**Backend Integration Lead:** `Sharun`  
**Frontend Integration Lead:** `Tharun`  

---

## 🎯 1. Sovereign Architecture Overview

The MRPL AI Workbench operates in a strict **Air-Gapped Local Mode**. All computation, model inference, vector storage, and document processing remain 100% inside the MRPL refinery perimeter.

```
┌────────────────────────────────────────────────────────────────────────┐
│                   MRPL REFINERY ON-PREMISE BOUNDARY                    │
│                                                                        │
│   ┌─────────────────┐       ┌─────────────────┐                        │
│   │   Frontend UI   │◄─────►│   Backend API   │                        │
│   │ (Port 5173/Tharun)      │ (Port 8000/Sharun)                       │
│   └─────────────────┘       └────────┬────────┘                        │
│                                      │                                 │
│        ┌─────────────────────────────┼────────────────────────────┐    │
│        ▼                             ▼                            ▼    │
│  ┌───────────┐                 ┌───────────┐                ┌────────┐ │
│  │ Local LLM │                 │ Local VDB │                │ Local  │ │
│  │ (Ollama)  │                 │ (Native)  │                │ Storage│ │
│  └───────────┘                 └───────────┘                └────────┘ │
│                                                                        │
│   ══════════════════════════════════════════════════════════════════   │
│   [🛑 DATA-LEAKAGE FIREWALL] INTERCEPTS & BLOCKS EXTERNAL TRAFFIC      │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (Blocked)
                                    ▼
                ❌ Cloud AI APIs (OpenAI / Gemini / Anthropic)
```

---

## 🛡️ 2. Data-Leakage Firewall Implementation

### Application-Level vs. OS/Network Air-Gapping
- **Application-Level Firewall (`security/firewall.py`):**
  - Whitelists only local endpoints (`localhost`, `127.0.0.1`, `192.168.*`, `10.*`, `*.local`, `host.docker.internal`).
  - Actively rejects any cloud AI domains (`api.openai.com`, `generativelanguage.googleapis.com`, `api.anthropic.com`, etc.).
  - Increments security audit counter without leaking confidential document contents.
- **Operating System & Network Air-Gapping (`docker-compose.yml`):**
  - Docker bridge network can be configured with `internal: true` to block WAN gateway egress at the kernel level.
  - No internet connection or cloud API keys required.

---

## 🔌 3. Integration APIs for Sharun (Backend)

Sharun can expose the Sovereignty status to Tharun's frontend with two simple routes:

```python
from fastapi import APIRouter
from security import security_monitor

router = APIRouter(prefix="/api/sovereignty", tags=["Sovereignty & Security"])

@router.get("/status")
async def get_sovereignty_status():
    """Retrieve live air-gapped status and external call counts."""
    return security_monitor.get_status()

@router.get("/audit-logs")
async def get_audit_logs(limit: int = 50):
    """Retrieve sanitized security audit logs."""
    return security_monitor.get_audit_logs(limit=limit)
```

### Response Payload (`security_monitor.get_status()`):
```json
{
  "deployment_mode": "LOCAL_AIR_GAPPED",
  "external_calls": 0,
  "local_models": [
    "llama3-8b-instruct (Local Ollama @ localhost:11434)",
    "mistral-7b-instruct (Local vLLM @ localhost:8000)",
    "nomic-embed-text (Local On-Prem Embedder)"
  ],
  "local_vector_db": true,
  "internet_required": false,
  "security_status": "SECURE",
  "data_leaving_system": "None",
  "firewall_active": true,
  "blocked_attempts": 0
}
```

---

## 💻 4. Frontend Status Display (Tharun)

Tharun can query `/api/sovereignty/status` to render the top-level safety banner:

```
┌────────────────────────────────────────────────────────┐
│ 🟢 Local Mode | External Calls: 0 | Data Leaving: None │
└────────────────────────────────────────────────────────┘
```

---

## 🚀 5. Local Startup Instructions

### Method A: Native Local Execution
1. **Start Ollama Local Model Runtime:**
   ```bash
   ollama run llama3:8b-instruct
   ```
2. **Start Backend API:**
   ```bash
   cd backend
   uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
3. **Start Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

### Method B: Docker Compose Air-Gapped Deployment
```bash
docker-compose -f deploy/docker-compose.yml up -d
```

---

## 🧪 6. Demo Procedure: Proving the Sovereign Claim

Run the automated live demonstration script to prove the sovereign guarantee to judges:

```bash
python deploy/verify_sovereignty_demo.py
```

### What the demo proves:
1. **Local Document Ingestion:** Processes PDF into local page assets without cloud OCR.
2. **Local Vector Search:** Queries local corpus with 0.07 ms sub-millisecond latency.
3. **Local Claim Verification:** Verifies finding against sensor telemetry locally.
4. **Cloud AI Blocking:** Simulates unauthorized calls to OpenAI and Gemini API endpoints; proves that the Data-Leakage Firewall intercepts and blocks them, keeping `External Calls = 0`.
5. **Audit Trail:** Shows clean audit logs in `logs/sovereignty_audit.log` with zero confidential text leakage.
