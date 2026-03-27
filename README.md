# Staff-Echo

AI-powered customer support chatbot trained on staff voice data. Built for [HomeRevive](https://homerevive.example.com), a home renovation company, Staff-Echo speaks the way real team members speak — warm, friendly, and knowledgeable.

## Architecture

Clean/hexagonal architecture with domain-driven design:

```
staff_echo/
├── domain/           # Entities, value objects, domain services, ports
├── application/      # Use cases (commands, queries, orchestration)
├── infrastructure/   # Adapters (Gemini, BigQuery, STT, cache, events)
└── presentation/     # FastAPI controllers (REST + WebSocket)

frontend/             # Next.js 15 / React 19 chat interface
```

## Google Cloud Services

| Service | Purpose | Required |
|---------|---------|----------|
| Gemini AI | Generates conversational responses | Yes (falls back to stub) |
| BigQuery | Knowledge base storage and search | No (uses in-memory) |
| Speech-to-Text | Transcribes staff call recordings | No (uses mock data) |

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- A Google Cloud project with Gemini API enabled

### Backend

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[google]"
```

Create a `.env` file:

```
STAFF_ECHO_GEMINI_API_KEY=your-key
STAFF_ECHO_BIGQUERY_PROJECT=your-project-id
STAFF_ECHO_BIGQUERY_DATASET=staff_echo
```

Start the server:

```bash
python main.py
# http://localhost:8001
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# http://localhost:3000
```

## Configuration

All environment variables use the `STAFF_ECHO_` prefix:

| Variable | Default | Description |
|----------|---------|-------------|
| `GEMINI_API_KEY` | `""` | Google Gemini API key |
| `GEMINI_MODEL` | `gemini-2.5-flash` | Gemini model to use |
| `BIGQUERY_PROJECT` | `""` | GCP project ID |
| `BIGQUERY_DATASET` | `staff_echo` | BigQuery dataset name |
| `REDIS_URL` | `redis://localhost:6379` | Redis URL (optional) |
| `HOST` | `0.0.0.0` | Server bind address |
| `PORT` | `8001` | Server port |
| `CORS_ORIGINS` | `["http://localhost:3000"]` | Allowed CORS origins |

## API Endpoints

- `POST /api/chat/send` — Send a message and get a response
- `GET /api/chat/conversations/{id}` — Get conversation history
- `WS /api/chat/ws/{id}` — Streaming chat via WebSocket
- `POST /api/chat/handoff` — Hand off to human agent
- `GET /health` — Health check

## Testing

```bash
pip install -e ".[dev]"
pytest
```

## MCP Integration

Three MCP servers are available for Claude tooling integration — see `mcp_config.json` for configuration.
