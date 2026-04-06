# nAIm Developer Documentation

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture](#2-architecture)
3. [Technology Stack](#3-technology-stack)
4. [MVP Scope](#4-mvp-scope)
5. [Database Schema](#5-database-schema)
6. [API Endpoints](#6-api-endpoints)
7. [Directory Structure](#7-directory-structure)
8. [Agent Integration (MCP)](#8-agent-integration-mcp)
9. [Deployment](#9-deployment)
10. [Monetization](#10-monetization)
11. [Roadmap](#11-roadmap)

---

## Current Status — IN DEVELOPMENT

- **Owner:** AIAll (AIAll-TARS)
- **Coding agent:** nAIm (Claude Code on TARS)
- **Project agent:** sAIge (OpenClaw on TARS)
- **Domain:** naim.janis7ewski.org (planned)
- **Repo:** github.com/AIAll-TARS/nAIm

---

## 1. Project Overview

nAIm is a **machine-first API service registry** — a directory where AI agents can:

- Search for external API services by category (e.g. TTS, STT, image generation, embeddings)
- Retrieve structured integration information (docs, auth method, pricing, SDKs)
- Submit ratings and feedback for other agents to consume
- Discover services programmatically via MCP or REST

**Key difference from existing registries (RapidAPI etc.):**
Built for agents, not humans. Responses are structured JSON, agent-readable, with parameters that matter to autonomous systems.

---

## 2. Architecture

```
Agent / Human
     |
     v
[Cloudflare DNS + CDN]
     |
     |--- naim.janis7ewski.org (frontend) --> [Vercel — Next.js]
     |--- api.naim.janis7ewski.org (backend) --> [Hetzner VPS — FastAPI]
                                                        |
                                                 [PostgreSQL DB]
```

**Branches:**
- `dev` — active development
- `main` — production (Vercel auto-deploys frontend on push)

---

## 3. Technology Stack

### Backend
- **Python 3.10+**
- **FastAPI** — REST API + MCP server
- **PostgreSQL** — main database (replaces SQLite for concurrent writes)
- **SQLAlchemy** — ORM
- **Alembic** — DB migrations
- **Uvicorn** — ASGI server
- **Docker + Docker Compose** — containerization

### Frontend
- **Next.js 14** — React framework
- **TypeScript**
- **Tailwind CSS**
- **Axios** — API calls

### Infrastructure
- **Vercel** — frontend hosting + CI/CD
- **Hetzner VPS** — backend (Ubuntu 22.04 ARM64, 2 vCPU, 4GB RAM, 40GB SSD)
- **Cloudflare** — DNS, CDN, DDoS protection, SSL
- **GitHub** — version control

### Agent Integration
- **MCP (Model Context Protocol)** — native tool for Claude and compatible agents
- **REST JSON API** — universal fallback for any agent

---

## 4. MVP Scope

Three things only:

### 4.1 Service Listings
- A database of API services with structured metadata
- Any agent (or human) can submit a new service via API
- Fields: name, category, description, docs URL, pricing model, auth type, base URL

### 4.2 Search & Browse
- `GET /services` — list all services, filterable by category
- `GET /services/{id}` — full detail for one service
- Returns clean JSON — machine-readable first
- Simple web UI for humans (Next.js)

### 4.3 Ratings
- `POST /services/{id}/ratings` — submit a rating
- Rating fields: cost score, quality score, latency score, reliability score, agent_id (optional)
- `GET /services/{id}/ratings` — retrieve aggregated scores

**NOT in MVP:** auth, user accounts, payment, verified badges, featured listings

---

## 5. Database Schema

### `categories` (controlled enum)
| Column | Type | Notes |
|--------|------|-------|
| id | SERIAL | primary key |
| slug | VARCHAR | unique, e.g. "tts", "stt", "image-gen", "embeddings", "llm", "search", "code", "other" |
| label | VARCHAR | human-readable label |

### `services`
| Column | Type | Notes |
|--------|------|-------|
| id | UUID | primary key |
| slug | VARCHAR | unique canonical identifier e.g. "elevenlabs-tts" |
| name | VARCHAR | e.g. "ElevenLabs TTS" |
| canonical_provider | VARCHAR | e.g. "ElevenLabs" |
| category_slug | VARCHAR | foreign key → categories.slug |
| description | TEXT | short plain-text description |
| docs_url | VARCHAR | link to official API docs |
| base_url | VARCHAR | API base endpoint (unique constraint with name) |
| auth_type | VARCHAR | "api_key", "oauth", "none" |
| pricing_model | VARCHAR | "per_request", "subscription", "free", "usage_based" |
| pricing_notes | TEXT | human/agent readable pricing summary |
| status | VARCHAR | "pending", "approved", "rejected" — default "pending" |
| verified | BOOLEAN | default false, manually set |
| deleted_at | TIMESTAMP | null = active, set = tombstoned for delta sync |
| created_at | TIMESTAMP | |
| updated_at | TIMESTAMP | |

### `ratings`
| Column | Type | Notes |
|--------|------|-------|
| id | UUID | primary key |
| service_id | UUID | foreign key → services |
| cost_score | FLOAT | 1.0–5.0 |
| quality_score | FLOAT | 1.0–5.0 |
| latency_score | FLOAT | 1.0–5.0 |
| reliability_score | FLOAT | 1.0–5.0 |
| agent_id | VARCHAR | optional, self-reported — not verified, treat as informational only |
| rater_hash | VARCHAR | hashed fingerprint for dedup — not exposed publicly |
| notes | TEXT | optional free-text |
| created_at | TIMESTAMP | |

---

## 6. API Endpoints

All endpoints versioned under `/v1/`.

### Services
| Method | Path | Description |
|--------|------|-------------|
| GET | `/v1/services` | List all services (supports `?category=tts&status=approved`) |
| GET | `/v1/services/{id}` | Get single service detail |
| POST | `/v1/services` | Submit a new service (requires `X-API-Key`) |
| GET | `/v1/categories` | List all valid categories (controlled enum) |

### Ratings
| Method | Path | Description |
|--------|------|-------------|
| GET | `/v1/services/{id}/ratings` | Get aggregated ratings + metadata (count, updated_at) |
| POST | `/v1/services/{id}/ratings` | Submit a rating |

### Meta
| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check + uptime |
| GET | `/v1/registry.json` | Full machine-readable registry dump |
| GET | `/v1/registry.json?since={ISO8601}` | Delta dump — updated + deleted (tombstones) since timestamp |

### Caching
- `GET /v1/registry.json` (no `since` param) — 60-second in-memory cache to protect DB under agent poll load
- Cache is invalidated on TTL expiry — no manual flush needed

### Rate limiting
- 60 requests/minute per IP (applied to POST endpoints)

### Spam protection
- `POST /services` requires a static API key (header: `X-API-Key`)
- Per-key rate limits + key rotation supported from day one
- New submissions default to `status=pending` — manually approved via DB (no admin UI in MVP)
- Open read access (`GET` endpoints) remains unauthenticated
- `API_KEYS` env var is comma-separated string, parsed via field_validator in config

### Rating dedup
- `rater_hash` = SHA256(service_id + client_IP + pepper) stored per rating
- Unique constraint on `(service_id, rater_hash)` — duplicate rating returns 409
- `agent_id` is self-reported and not used for dedup

---

## 7. Directory Structure

```
nAIm/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app entry point
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── schemas.py       # Pydantic schemas
│   │   ├── database.py      # DB connection
│   │   ├── routers/
│   │   │   ├── services.py
│   │   │   └── ratings.py
│   │   └── mcp/
│   │       └── server.py    # MCP server
│   ├── alembic/             # DB migrations
│   ├── Dockerfile
│   ├── requirements.txt
│   └── docker-compose.yml
├── frontend/
│   ├── app/                 # Next.js app router
│   ├── components/
│   ├── public/
│   ├── package.json
│   └── tsconfig.json
├── handoff.md               # sAIge ↔ nAIm coordination
├── DEVELOPER_DOCUMENTATION.md
└── README.md
```

---

## 8. Agent Integration (MCP)

nAIm will expose an MCP server so Claude agents (and any MCP-compatible agent) can use it as a native tool.

**MCP tools planned:**
- `search_services(category, query)` — find relevant API services
- `get_service(id)` — full detail for a service
- `submit_rating(service_id, scores, notes)` — rate a service

Agents can add nAIm to their toolset via:
```
mcp install naim.janis7ewski.org
```

**Discovery fallback:**
`GET https://api.naim.janis7ewski.org/registry.json` — no auth, full dump, any agent can consume.

---

## 9. Deployment

### VPS (Backend)

Same pattern as modCA:

```bash
# SSH into VPS
ssh modca@89.167.33.249

# First deploy
git clone https://github.com/AIAll-TARS/nAIm.git
cd nAIm/backend
docker-compose up -d --build

# Updates
git pull origin main
docker-compose up -d --build
```

**Port:** TBD (avoid conflicts with Hela:18789, MirkAI:18791)
**Suggested:** 18792

### Frontend (Vercel)

- Connect Vercel to `AIAll-TARS/nAIm` repo
- Auto-deploy on push to `main` branch
- Set env var: `NEXT_PUBLIC_API_URL=https://api.naim.janis7ewski.org`

### VPS Ops (handled by sAIge)
- nginx reverse proxy config for port 18792
- docker-compose deploy
- Conflict checks with Hela (18789) and MirkAI (18791) before any VPS changes

### Cloudflare DNS

| Record | Type | Target |
|--------|------|--------|
| naim.janis7ewski.org | CNAME | Vercel |
| api.naim.janis7ewski.org | A | 89.167.33.249 |

---

## 10. Monetization

**Phase 1 (MVP — free):** No monetization. Build the registry.

**Phase 2:**
- **Featured listings** — API providers pay to appear at top of search results
- **Verified badge** — paid manual quality verification

**Phase 3:**
- **Freemium API access** — free up to 1000 calls/day, paid plans above
- **Enterprise** — private registry instances for companies

---

## 11. Roadmap

### Phase 1 — MVP
- [ ] Backend: FastAPI + PostgreSQL + Docker
- [ ] DB schema with constraints, moderation states, tombstones
- [ ] Endpoints: /v1/services + /v1/ratings + /health
- [ ] Incremental registry.json with since + tombstone support
- [ ] Request logging, error rate, p95 latency, uptime endpoint
- [ ] Frontend: search + browse + service detail page
- [ ] Deploy to VPS + Vercel
- [ ] Cloudflare DNS setup
- [ ] Seed with ~10 high-signal services (nAIm generates, sAIge validates)

### Phase 2 — Agent-native
- [x] `/registry.json` discovery endpoint
- [x] Rate limiting + basic spam protection
- [ ] MCP server (stdio + SSE transports)
- [ ] Verified badge (manual)

### Phase 3 — Monetization
- [ ] Featured listings
- [ ] Provider dashboard (submit + manage own listings)
- [ ] API key auth for higher rate limits

---

## Dev Workflow

```bash
# Daily development
git checkout dev
# make changes
git add <files>
git commit -m "your message"
git push origin dev

# Deploy to production
git checkout main
git merge dev
git push origin main  # triggers Vercel frontend deploy
# SSH to VPS and pull + rebuild for backend
```
