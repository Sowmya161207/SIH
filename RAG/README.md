# MRPL RAG Pipeline
### Sovereign On-Premise Retrieval-Augmented Generation System
**SIH26117 | RAG Engineer: Meenaloshini**

> **Fully local. No cloud APIs. No external LLMs. Runs offline after first model download.**

---

## Architecture

```
PDF
 ↓  PyMuPDF (fitz)
Text Extraction (page-by-page)
 ↓  cleaner.py
Cleaning (whitespace, hyphens, control chars)
 ↓  chunker.py
Chunking (400-char sliding window, 80-char overlap)
 ↓
Metadata Attachment (document_id, page, equipment, allowed_roles …)
 ↓  sentence-transformers / all-MiniLM-L6-v2
Embeddings (384-dim, CPU, ~80MB model)
 ↓  FAISS FlatIP
Local Vector Database (persisted to disk)
 ↓
Similarity Search + Permission Filter
 ↓
Evidence + Source Citation
```

---

## Quick Start

### 1. Install dependencies
```bash
cd RAG
pip install -r requirements.txt
```

> **First run:** the embedding model (~80MB) is downloaded automatically from HuggingFace.
> After that, fully offline.

### 2. Generate demo industrial documents
```bash
python data/demo/generate_demo_docs.py
```
Creates 4 realistic PDFs in `data/demo/`:
- `maintenance_report_p101.pdf`
- `equipment_manual_p101.pdf`
- `sop_pump_maintenance.pdf`
- `incident_report_p101.pdf`

### 3. Ingest documents into the vector store
```bash
# Ingest all 4 demo PDFs
python ingest_documents.py --pdf_dir data/demo/

# Check store stats
python ingest_documents.py --stats
```

### 4. Run a search (smoke test)
```bash
python rag_services.py
```

### 5. Run tests
```bash
python -m pytest tests/ -v
```

---

## Backend Integration (for Sharun)

Import a single file:

```python
from rag_services import search_documents, ingest_pdf, get_store_stats
```

### `search_documents(query, user_role=None, top_k=5)`

```python
from rag_services import search_documents

result = search_documents(
    query     = "bearing temperature exceeded alarm",
    user_role = "maintenance_engineer",   # or None to bypass ACL
    top_k     = 5,
)

# result structure:
{
    "query":   "bearing temperature exceeded alarm",
    "role":    "maintenance_engineer",
    "evidence": [
        {
            "source":        "maintenance_report_p101.pdf",
            "page":          3,
            "text":          "… bearing temp rose to 87°C on 28 May …",
            "score":         0.91,
            "document_id":   "maint_report_p101",
            "title":         "Pump P-101 Maintenance Report",
            "equipment":     "Pump P-101",
            "document_type": "maintenance",
            "classification":"internal",
        },
        # …up to top_k results
    ],
    "total_found":    12,   # before role filter
    "total_returned":  5,   # after role filter, capped at top_k
}
```

### `ingest_pdf(pdf_path, metadata, reset_store=False)`

```python
from rag_services import ingest_pdf

result = ingest_pdf(
    pdf_path = "data/raw/new_report.pdf",
    metadata = {
        "document_id":   "new_report_2025",
        "title":         "New Equipment Report",
        "equipment":     "Pump P-101",
        "document_type": "maintenance",
        "classification":"internal",
        "allowed_roles": ["maintenance_engineer", "manager"],
    }
)
# result: {"status": "ok", "chunks_added": 42, "document_id": "new_report_2025"}
```

### `get_store_stats()`
```python
from rag_services import get_store_stats
stats = get_store_stats()
# {"total_vectors": 384, "index_exists": True, ...}
```

---

## Permission Model

| `user_role` | Access |
|---|---|
| `None` | Bypass ACL — all documents (trusted backend call) |
| `"maintenance_engineer"` | maintenance + manual + SOP docs |
| `"operator"` | manual + SOP docs |
| `"safety_officer"` | SOP + incident reports |
| `"manager"` | All documents |

Access is chunk-level: every chunk carries `allowed_roles`. A user only sees chunks where their role appears in `allowed_roles`.

---

## Document Metadata Schema

```json
{
  "document_id":   "maint_report_p101",
  "title":         "Pump P-101 Maintenance Report — Q2 2025",
  "page":          3,
  "equipment":     "Pump P-101",
  "document_type": "maintenance",
  "classification":"internal",
  "allowed_roles": ["maintenance_engineer", "manager"]
}
```

---

## File Structure

```
RAG/
├── rag/
│   ├── config.py                ← All tunable parameters
│   ├── ingestion/
│   │   ├── pdf_extractor.py     ← PyMuPDF extraction
│   │   ├── cleaner.py           ← Text normalization
│   │   └── chunker.py           ← Sliding-window chunker
│   ├── embeddings/
│   │   └── embedder.py          ← sentence-transformers wrapper
│   ├── vector_store/
│   │   ├── faiss_store.py       ← FAISS index (persist / load / search)
│   │   ├── faiss.index          ← [generated] FAISS binary index
│   │   └── metadata.pkl         ← [generated] chunk metadata
│   ├── retrieval/
│   │   └── retriever.py         ← search_documents() + ACL
│   └── models/
│       └── README.md            ← Model download instructions
├── data/
│   ├── raw/                     ← Drop your PDFs here
│   └── demo/
│       ├── generate_demo_docs.py
│       └── *.pdf                ← [generated] 4 demo PDFs
├── tests/
│   ├── test_ingestion.py
│   ├── test_embeddings.py
│   └── test_retrieval.py
├── rag_services.py              ← PUBLIC API (Sharun imports this)
├── ingest_documents.py          ← CLI ingestion tool
├── requirements.txt
└── README.md
```

---

## Technology Stack

| Component | Technology | Why |
|---|---|---|
| PDF extraction | PyMuPDF (fitz) | Fast, accurate, fully local |
| Embeddings | sentence-transformers `all-MiniLM-L6-v2` | 80MB, CPU-only, Apache 2.0 |
| Vector DB | FAISS (faiss-cpu) | Battle-tested, persistent, no server needed |
| Language | Python 3.10+ | Standard |

**Zero cloud dependencies. Zero API keys. Zero data leaves the premises.**
