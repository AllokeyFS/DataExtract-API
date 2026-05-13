# DataExtract API

A multiformat intelligent data extraction service powered by a local LLM (Mistral 7B via Ollama). Accepts unstructured text and returns structured JSON — no external API calls, fully offline.

## What it does

- **Resume** → extracts name, email, skills, experience, education
- **Invoice** → extracts vendor, client, line items, total
- **Email** → extracts sender, intent, action items, urgency
- **Auto-detection** — omit `doc_type` and the service detects the format automatically

## Architecture

```
Client
  │
  ▼
FastAPI (REST API)
  │
  ├── POST /extract   → Parser Service → Ollama (Mistral 7B)
  ├── GET  /history   → PostgreSQL
  └── GET  /health
```

## Tech Stack

- **FastAPI** — async REST API
- **Ollama + Mistral 7B** — local LLM inference (no external API needed)
- **PostgreSQL** — persistent storage of extraction history
- **SQLAlchemy** — ORM
- **Docker + Docker Compose** — full containerization
- **pytest** — unit and integration tests

## Getting Started

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Ollama](https://ollama.com) with Mistral pulled locally:

```bash
ollama pull mistral
```

### Run with Docker

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/dataextract-api
cd dataextract-api

# Configure environment
cp .env.example .env
# Edit .env and set your DATABASE_URL password

# Start all services
docker-compose up --build
```

API will be available at `http://localhost:8000`  
Interactive docs at `http://localhost:8000/docs`

### Run locally (without Docker)

```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/extract` | Extract structured data from text |
| `GET` | `/history` | List past extractions |
| `GET` | `/history/{id}` | Get specific extraction by ID |
| `GET` | `/health` | Service health check |

### Example Request

```bash
curl -X POST http://localhost:8000/extract/ \
  -H "Content-Type: application/json" \
  -d '{
    "text": "John Doe, Software Engineer. Email: john@example.com. Skills: Python, Docker.",
    "doc_type": "resume"
  }'
```

### Example Response

```json
{
  "id": 1,
  "doc_type": "resume",
  "data": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": null,
    "skills": ["Python", "Docker"],
    "experience": [],
    "education": []
  }
}
```

## Running Tests

```bash
pytest tests/ -v
```

## Design Decisions

- **Local LLM over cloud API** — no cost, no data privacy concerns, works fully offline
- **Auto-detection** — keyword-based format detection before hitting the model, reduces unnecessary inference
- **JSON extraction with fallback parsing** — model output is sanitized to handle markdown fences and extra text that local models sometimes produce
- **Async throughout** — FastAPI + httpx async client keeps the service non-blocking under concurrent requests
