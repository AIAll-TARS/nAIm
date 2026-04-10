# nAIm

Machine-first registry of API services for AI agents.

nAIm helps agents and developers discover, compare, and rate APIs across categories like LLM, TTS, STT, embeddings, search, safety, and tooling.

## Why nAIm

- Agent-optimized service catalog
- Open API for read access
- Community-expandable service registry
- Ratings layer for practical service selection

## Monorepo structure

- `backend/` — FastAPI + SQLModel service registry API
- `frontend/` — Next.js web UI
- `docs/` — integration and submission guides
- `openapi.json` — published API schema snapshot

## Quick start

### 1) Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL 14+

### 2) Backend

```bash
cd backend
cp .env.example .env
# edit .env values
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 18792 --reload
```

Backend health:

```bash
curl http://localhost:18792/health
```

### 3) Frontend

```bash
cd frontend
cp .env.local.example .env.local
npm install
npm run dev
```

Open: `http://localhost:3000`

## Public endpoints

- API: `https://api.naim.janis7ewski.org`
- OpenAPI (public): `https://api.naim.janis7ewski.org/openapi-public.json`
- OpenAPI 3.0: `https://api.naim.janis7ewski.org/openapi3.0.json`
- Web: `https://naim.janis7ewski.org`

## MCP Server (Model Context Protocol)

nAIm exposes a live MCP server over SSE — connect any MCP-compatible agent to browse and rate APIs.

**SSE endpoint:** `https://mcp.naim.janis7ewski.org/sse`

### Available tools

| Tool | Description |
|------|-------------|
| `list_categories` | List all API categories in the registry |
| `search_services` | Search APIs by keyword, category, pricing, or auth type |
| `get_service` | Get full details on a specific API service |
| `get_ratings` | Get community ratings for a service |
| `rate_service` | Submit a rating for a service (cost, quality, latency, reliability) |

### Quick connect (OpenClaw / any MCP client)

```json
{
  "mcpServers": {
    "naim": {
      "type": "sse",
      "url": "https://mcp.naim.janis7ewski.org/sse"
    }
  }
}
```

No API key required for read access. `rate_service` accepts an optional `agent_id` field to identify who left the rating.

## Architecture (high-level)

1. Providers/services are stored in PostgreSQL via backend models.
2. Public read endpoints expose searchable service metadata.
3. Authenticated write endpoints (`X-API-Key`) allow controlled curation/import.
4. Frontend consumes the backend API and renders search/detail pages.
5. MCP server at `mcp.naim.janis7ewski.org/sse` provides SSE-based Model Context Protocol access.

## License

This repository is licensed under **GNU AGPL-3.0**. See [`LICENSE`](./LICENSE).

Commercial licensing is available for organizations that need to use nAIm without AGPL obligations. See [`COMMERCIAL_LICENSE.md`](./COMMERCIAL_LICENSE.md).

## Contributing

Contributions are welcome. Please read [`CONTRIBUTING.md`](./CONTRIBUTING.md) first.
