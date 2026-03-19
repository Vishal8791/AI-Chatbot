# AI Chatbot API

Production-ready FastAPI chatbot powered by Claude with per-session conversation memory.

## Quick Start

```bash
# 1. Clone and install
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Edit .env and set ANTHROPIC_API_KEY

# 3. Run
uvicorn app.main:app --reload
```

Open **http://localhost:8000/docs** for the interactive API playground.

## Docker

```bash
docker compose up --build
```

## Testing

```bash
pytest tests/ -v
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/health` | Liveness probe |
| `POST` | `/api/v1/chat/` | Send a message |
| `GET` | `/api/v1/chat/{session_id}/history` | Session info |
| `DELETE` | `/api/v1/chat/{session_id}` | Clear session |

## Example Request

```bash
curl -X POST http://localhost:8000/api/v1/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "my-session",
    "message": "What is the capital of France?",
    "system_prompt": "You are a helpful geography tutor."
  }'
```