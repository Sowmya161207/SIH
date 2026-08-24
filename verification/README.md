# Claim Verification & Evidence Layer (SIH26117)

**Project:** Sovereign On-Premise Agentic AI Workbench for MRPL (Mangalore Refinery and Petrochemicals Limited)  
**Role:** Verification & Evidence Layer (`Yoagesh`)  
**Backend Integration Contact:** `Sharun`

---

## 🎯 Purpose
The Verification Layer validates AI findings against Ground-Truth Evidence (RAG knowledge base + real-time sensor analytics). It provides explainable, deterministic claim classification to distinguish:
- **`SUPPORTED`**: Direct, unambiguous evidence corroborates the finding.
- **`INFERRED`**: Multi-source indirect evidence (e.g. vibration increase + overdue inspection + OEM manual cause) supports a probabilistic hypothesis.
- **`UNSUPPORTED`**: Recorded evidence or physical inspection explicitly contradicts the finding.
- **`INSUFFICIENT_EVIDENCE`**: Lack of sensor data or RAG documentation to prove or disprove the assertion.

---

## 📁 Module Structure

```
verification/
├── __init__.py               # Package exports
├── schemas.py                # Data classes, enums & serialization
├── claim_extraction.py       # Atomic claim segmenter & modality analyzer
├── evidence_matching.py      # Semantic matcher, causal parser & contradiction detector
├── verifier.py               # Core orchestrator and verify_claims() function
├── README.md                 # Integration documentation
└── tests/
    ├── __init__.py
    ├── test_claim_extraction.py
    ├── test_evidence_matching.py
    └── test_verifier.py
```

---

## 🚀 Usage Guide for Backend (`Sharun`)

### 1. Basic Import
```python
from verification import verify_claims
```

### 2. Single Finding Verification (MRPL Example)
```python
finding = "Possible bearing degradation."

evidence = [
    "Vibration increased 35%",
    "Bearing inspection overdue",
    "Equipment manual lists bearing wear as a possible cause"
]

result = verify_claims(finding, evidence)
print(result)
```

**Output:**
```json
{
  "claim": "Possible bearing degradation.",
  "status": "INFERRED",
  "confidence": 0.78,
  "supporting_evidence": [
    "Vibration increased 35%",
    "Bearing inspection overdue",
    "Equipment manual lists bearing wear as a possible cause"
  ],
  "reason": "Indirect evidence supports the possibility.",
  "limitations": [
    "No physical bearing inspection available."
  ]
}
```

---

### 3. Batch Verification with RAG & Sensor Payloads
```python
from verification import verify_claims

findings = [
    "Vibration increased 35% on P-101",
    "Possible bearing degradation.",
    "Cooling water valve V-302 stuck open"
]

evidence = [
    {"text": "Sensor: Vibration increased 35% on P-101", "source": "Sensor"},
    {"text": "RAG: Equipment manual lists bearing wear as a cause of vibration", "source": "RAG"},
    {"text": "Maintenance log: Bearing inspection overdue", "source": "Maintenance"}
]

results = verify_claims(findings, evidence)
# Returns a List[Dict] with status for each claim
```

---

## 🧪 Running Unit Tests
```bash
python -m unittest discover verification/tests
```
