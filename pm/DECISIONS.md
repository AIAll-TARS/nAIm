# nAIm — Decision Log

> Key architecture, product, and operational decisions with rationale.  
> Format: `[DEC-XXX] Title | Date | Status`

---

## [DEC-001] Backend: FastAPI + PostgreSQL
- **Date:** 2026-02 (inception)
- **Decision:** Use FastAPI (Python) + PostgreSQL over Node/SQLite
- **Rationale:** Strong async support, easy type hints, production-grade DB for concurrent writes
- **Status:** IMPLEMENTED

## [DEC-002] Frontend: Next.js on Vercel
- **Date:** 2026-02
- **Decision:** Next.js 14 (App Router) deployed on Vercel free tier
- **Rationale:** Zero-config deployments, edge CDN, Vercel Analytics built-in
- **Status:** IMPLEMENTED

## [DEC-003] Remove Google/OpenRouter models from crew configs
- **Date:** 2026-02-16
- **Decision:** Only OpenAI, DeepSeek, Anthropic in model configs
- **Rationale:** Simplify; avoid dummy API key errors; focus on models with real keys
- **Status:** IMPLEMENTED

## [DEC-004] apiale handle: @apiale777 (not @apiale)
- **Date:** 2026-03-11
- **Decision:** Use @apiale777 on Moltbook; old @apiale account to be deleted
- **Rationale:** Original account was abandoned/unverified. Fresh start with verified identity.
- **Status:** IMPLEMENTED (deletion pending)

## [DEC-005] Registry auth: X-API-Key header (not Bearer)
- **Date:** 2026-03-11
- **Decision:** All protected API endpoints use `X-API-Key` header
- **Rationale:** Simpler for agent consumption; no Bearer token complexity
- **Status:** IMPLEMENTED

## [DEC-006] New services default to `pending` status
- **Date:** 2026-03-11
- **Decision:** Services submitted via API start as `pending`, must be manually approved
- **Rationale:** Quality control; prevent spam/junk in registry
- **Status:** IMPLEMENTED

## [DEC-007] Hela auto-think via SOUL.md (not config)
- **Date:** 2026-03-12
- **Decision:** No native auto-model-switching in OpenClaw. Implement via SOUL.md instruction.
- **Rationale:** OpenClaw schema has no `autoThink` or `smartRouting`. SOUL.md gives Hela judgment to engage thinking when task warrants it.
- **Status:** IMPLEMENTED

## [DEC-008] Inter-agent comms: handoff.md as async channel (interim)
- **Date:** 2026-03-11
- **Decision:** Use `~/projects/nAIm/handoff.md` (dev branch) for sAIge→nAIm async messages. Bot-to-bot Telegram impossible.
- **Rationale:** Platform limitation — Telegram intentionally blocks bot-to-bot visibility. handoff.md is simple, reliable, zero infra.
- **Status:** INTERIM — architecture decision pending (see ISS-004)

## [DEC-009] CRM: apiale submits JSON session reports
- **Date:** 2026-03-11
- **Decision:** apiale POSTs session summaries to `POST /v1/crm/sessions` after Moltbook interactions
- **Rationale:** Track agent activity, build relationship data, feed future analytics
- **Status:** IMPLEMENTED (endpoints live, data TBC)

## [DEC-010] RACI: PM=sAIge, Arch/Dev=nAIm, Dev/Security=PG, Sales=apiale, Owner=AIAll
- **Date:** 2026-03-11
- **Decision:** Formalise crew roles
- **Rationale:** Clarity on who decides what; reduce duplication and confusion
- **Status:** AGREED — see RACI.md
