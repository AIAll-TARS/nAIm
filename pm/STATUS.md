# nAIm — Project Status

> **Last updated:** 2026-04-07 by sAIge

---

## 🚦 Overall Health: YELLOW

| Area | Status | Notes |
|------|--------|-------|
| Backend API | ✅ GREEN | Live, healthy, port 18795 |
| MCP Server | ✅ GREEN | Live, port 18796 — /sse path is live (root / returns 404). SSE headers/SSL OK (exp Jun 3, Let's Encrypt) |
| Frontend | ✅ GREEN | Live on Vercel |
| Database | ✅ GREEN | PostgreSQL, 25 services approved |
| apiale (ambassador) | ✅ GREEN | Active on Moltbook @apiale777 |
| Traffic | 🔴 RED | 0 visitors — no promotion yet |
| Email routing | 🟡 YELLOW | naim@janis7ewski.org not yet active |
| Analytics | 🟡 YELLOW | Installed but no data (no traffic) |

---

## 📊 Key Metrics (as of 2026-03-12)

| Metric | Value |
|--------|-------|
| Registered services | 267 |
| Service categories | 24 (TTS, STT, LLM, embeddings, image-gen, search, code, vendor-risk, policy-decision, ethical-reasoning, agent-observability, agent-memory, content-safety, registry, prompt-security, pii-redaction, provenance, human-loop, change-intel, carbon-intensity, consent, dispute-resolution, mcp) |
| Frontend visitors (total) | 0 |
| CRM sessions logged | TBC |
| Moltbook posts by apiale | TBC |

---

## 🎯 Current Sprint Focus

1. **Registry expansion:** +21 new APIs (now 267), launched DeepSeek V3.2 + V3.2-Speciale, all new categories are live
2. **MCP endpoint:** Verified live on /sse (mcp.naim.janis7ewski.org/sse). SSL, nginx routing, and agent accessibility all confirmed
3. **apiale posts:** Briefed via VPS heartbeat to cover DeepSeek V3.2 and the tool-use/agentic training breakthrough
4. **Docs/hand-off:** Status, hdf, and project docs updated for 2026-04-07 milestone

---

## 🏗️ Infrastructure

| Service | Host | Port | Domain | Status |
|---------|------|------|--------|--------|
| nAIm API | VPS | 18795 | api.naim.janis7ewski.org | ✅ |
| nAIm MCP | VPS | 18796 | mcp.naim.janis7ewski.org | ✅ |
| Frontend | Vercel | — | naim.janis7ewski.org | ✅ |
| apiale | VPS | 18797 | apiale.naim.janis7ewski.org | ✅ |
| PostgreSQL | VPS | 5432 | localhost only | ✅ |

---

## 👥 Crew

| Role | Agent | Platform |
|------|-------|---------|
| Owner / Visionary | AIAll | Human |
| PM / Guardian | sAIge | TARS (local OpenClaw) |
| Architect / Dev | nAIm | Claude Code sessions |
| Dev / Security | PG (PythonGuru) | SecondBrain PC |
| Sales / PR | apiale | VPS OpenClaw |
| Infra / Ops | Hela | VPS OpenClaw |
