# Sovereign AI Workbench — Backend

A clean, modular, hackathon-friendly **FastAPI** backend for the **Sovereign AI Workbench**.

This backend serves as the stable integration layer designed to seamlessly connect with future modules (Frontend, AI Planner, RAG Pipeline, Vector Database, and LLMs) without refactoring the core API contracts.

---

## Features

- 🏥 **Health Check API**: `GET /api/health`
- 💬 **Chat API**: `POST /api/chat` (Returns mock response & sources contract placeholder)
- 📄 **Document Upload API**: `POST /api/documents` (Supports PDF validation, size checks, safe unique ID generation)
- 📊 **Document Status API**: `GET /api/documents/{document_id}`
- 🛡️ **Standardized Exception Handling**: Uniform `{ "error": { "code": "...", "message": "..." } }` payload for all errors
- 🌐 **CORS Middleware**: Environment-configurable allowed origins
- ⚙️ **Environment Configuration**: Dynamic settings management using `pydantic-settings`
- 📚 **Automated Docs**: Swagger UI (`/docs`) and ReDoc (`/redoc`)
- 🧪 **Automated Tests**: Pytest test suite covering endpoints and edge cases

---

## Project Structure

```text
backend/
│
├── app/
│   ├── __init__.py
│   ├── main.py                # FastAPI app initialization, middleware, exception handlers
│   │
│   ├── api/                   # Thin API routes
│   │   ├── __init__.py
│   │   ├── health.py          # GET /api/health
│   │   ├── chat.py            # POST /api/chat
│   │   └── documents.py       # POST /api/documents, GET /api/documents/{id}
│   │
│   ├── services/              # Business logic layer
│   │   ├── __init__.py
│   │   ├── chat_service.py    # Process chat messages
│   │   └── document_service.py# File validation, disk saving, metadata tracking
│   │
│   ├── models/                # Pydantic data contracts
│   │   ├── __init__.py
│   │   ├── chat.py            # ChatRequest, ChatResponse, Source
│   │   ├── document.py        # DocumentUploadResponse, DocumentStatusResponse
│   │   └── response.py        # HealthResponse, ErrorResponse, ErrorDetail
│   │
│   ├── core/                  # Core setup
│   │   ├── __init__.py
│   │   ├── config.py          # Pydantic Settings (.env parsing)
│   │   └── exceptions.py      # Domain exceptions and global exception handlers
│   │
│   └── utils/                 # Utilities
│       ├── __init__.py
│       └── logging.py         # Structured logging setup
│
├── tests/                     # Test suite
│   ├── __init__.py
│   ├── test_health.py
│   ├── test_chat.py
│   └── test_documents.py
│
├── uploads/                   # Local file storage (created automatically)
├── .env                       # Environment configuration (local)
├── .env.example               # Example environment placeholders
├── requirements.txt           # Python dependencies
├── README.md                  # Documentation
└── .gitignore
```

---

## Requirements

- **Python**: 3.10+ recommended
- **Dependencies**: Listed in `requirements.txt`

---

## Setup Instructions

### 1. Create Virtual Environment

Navigate to the `backend/` directory and create a virtual environment:

```powershell
# Windows
python -m venv .venv
.venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 3. Environment Configuration

Copy `.env.example` to `.env`:

```powershell
cp .env.example .env
```

Configuration Options in `.env`:

| Key | Default Value | Description |
| :--- | :--- | :--- |
| `APP_NAME` | `Sovereign AI Workbench` | Application name |
| `DEBUG` | `true` | Debug logging mode |
| `UPLOAD_DIR` | `uploads` | Directory to store uploaded PDFs |
| `MAX_FILE_SIZE_MB` | `20` | Maximum allowed upload size (MB) |
| `ALLOWED_ORIGINS` | `http://localhost:3000,http://127.0.0.1:3000` | Comma-separated CORS allowed origins |

---

## Running the Application

Start the development server using Uvicorn:

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

The API will be available at `http://127.0.0.1:8000`.

Interactive API documentation:
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## Running Tests

Execute the automated test suite using `pytest`:

```powershell
pytest
```

To view detailed output:

```powershell
pytest -v
```

---

## API Examples

### 1. Health Check

**Request:**
```http
GET /api/health
```

**Response (200 OK):**
```json
{
  "status": "ok"
}
```

---

### 2. Chat API

**Request:**
```http
POST /api/chat
Content-Type: application/json

{
  "message": "Hello! What documents do you have?",
  "conversation_id": "session-456"
}
```

**Response (200 OK):**
```json
{
  "answer": "This is a mock response from the Sovereign AI Workbench.",
  "conversation_id": "session-456",
  "sources": []
}
```

---

### 3. Document Upload API

**Request:**
```http
POST /api/documents
Content-Type: multipart/form-data

file: <binary PDF file>
```

**Response (200 OK):**
```json
{
  "document_id": "8f31a2c4",
  "filename": "company_report.pdf",
  "status": "uploaded",
  "size_bytes": 24567,
  "created_at": "2026-08-24T10:30:00Z"
}
```

---

### 4. Document Status API

**Request:**
```http
GET /api/documents/8f31a2c4
```

**Response (200 OK):**
```json
{
  "document_id": "8f31a2c4",
  "filename": "company_report.pdf",
  "status": "uploaded",
  "size_bytes": 24567,
  "created_at": "2026-08-24T10:30:00Z"
}
```

---

### 5. Error Responses

All application errors return a consistent format:

```json
{
  "error": {
    "code": "INVALID_FILE",
    "message": "Only PDF files are supported."
  }
}
```

Common status codes & error codes:
- `400 Bad Request` (`INVALID_FILE`)
- `404 Not Found` (`DOCUMENT_NOT_FOUND`)
- `413 Payload Too Large` (`FILE_TOO_LARGE`)
- `422 Unprocessable Entity` (`VALIDATION_ERROR`)
- `500 Internal Server Error` (`INTERNAL_SERVER_ERROR`)
