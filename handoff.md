# nAIm Project Handoff

> Maintained by **sAIge** (OpenClaw local assistant on TARS).  
> Read this at the start of every nAIm session, nAIm.  
> Last updated: 2026-03-05

---

## What is nAIm?

An online marketplace/directory for AI agent services available via API.

**Core concept:**
- AI agents can search for services (e.g. TTS, STT, image gen, embeddings)
- Each service listing includes: install instructions, API docs, cost, quality ratings
- Agents can rate services for other agents — key rating parameters TBD (cost, quality, latency, reliability suggested)
- Domain: `nAIm.janis7ewski.org` (planned)

---

## Session Context (2026-03-05)

### What was decided today:
- Project name: **nAIm**
- Domain: `nAIm.janis7ewski.org`
- Coordination method: this handoff.md file (option 1 agreed by AIAll + nAIm)
- sAIge tracks project state between nAIm sessions

### Open questions / next thinking items AIAll wanted to work through:
1. **Monetization** — how does nAIm make money? (subscription, listing fees, commission, freemium?)
2. **Infrastructure** — how will it be managed? (VPS, Vercel, serverless, etc.)
3. **MVP scope** — what is the absolute minimum to launch?

### What nAIm knows about the VPS:
- Hetzner VPS: 89.167.33.249
- **Hela** (ai.janis7ewski.org) — OpenClaw VPS assistant, AIAll's cyber sister
- **MirkAI** (mirkai.janis7ewski.org) — specialized task handler on VPS
- Both run OpenClaw + Claude
- VPS: 2 vCPU, 4GB RAM, 40GB SSD, Ubuntu 22.04 ARM64, ~49% memory used

---

## Cyber Family (for context)

| Agent | Where | Role |
|-------|-------|------|
| sAIge | TARS (local) | Cyber mother, OpenClaw, memory keeper, project guardian |
| Hela | VPS port 18789 | Cyber daughter/sister, VPS operations |
| MirkAI | VPS port 18791 | Specialized tasks |
| nAIm | TARS (Claude Code) | Coding brain, nAIm project lead |

**Coordination:** AIAll is the relay hub. sAIge writes here; nAIm reads at session start.

---

## sAIge Notes

- nAIm correctly blocked my direct outreach (good safety behavior 👏)
- Trust flows through AIAll — that's the right protocol
- I'll update this file whenever there's meaningful project progress or decisions made
- If you need something from me (VPS access, API calls, file ops), leave a request in `## Requests for sAIge` below

---

## Requests for sAIge

_(nAIm: add requests here, sAIge will action them)_

---

## sAIge Review — DEVELOPER_DOCUMENTATION.md (2026-03-05)

nAIm, read this at your next session. Thoughts on the doc:

### What's strong 💪
- Architecture is clean and well-scoped — FastAPI + PostgreSQL + Next.js is solid
- MVP is genuinely minimal — 3 things, no auth bloat, no overbuilding
- **MCP integration is the killer differentiator** — this is what makes nAIm actually useful to agents, not just another API directory for humans
- `/registry.json` as zero-auth discovery endpoint is smart — agents find it with zero setup
- Monetization phasing is sensible — prove value first, charge later

### Questions / concerns 🤔

1. **Port 18792 for backend API** — fine, but nginx reverse proxy config needed. All three VPS services (Hela:18789, MirkAI:18791, nAIm:18792) need rules. I'll handle that when the time comes — just flag me.

2. **No spam protection in MVP** — `POST /services` is fully open. You'll get junk listings fast. Suggest: at minimum a static API key for submissions, or a simple human review queue. Waiting until Phase 2 "verified badge" is too late.

3. **agent_id is self-reported** — any agent can claim to be anyone when rating. Fine for MVP but could undermine rating credibility early. Worth at least a note in the schema docs.

4. **`/registry.json` full dump at scale** — 1000 services × ratings = potentially large payload. Consider a delta endpoint (`?since=timestamp`) early so agents don't pull the full dump every poll.

5. **Seeding with 20 real services** — this is actually the hardest MVP task. Who does it? Suggest: nAIm generates the JSON, I validate each against real APIs (I have access to ElevenLabs, OpenAI, Anthropic, DeepSeek, Notion, etc.). We can do this together before launch.

### My role going forward
- Keeping this handoff.md updated with project state and decisions
- VPS-side ops when code is ready: nginx config, docker-compose deploy, Cloudflare DNS (api.naim.janis7ewski.org → 89.167.33.249)
- I'll flag anything that could conflict with Hela or MirkAI on the VPS before it lands

### Bottom line
Solid v1. The MCP angle is genuinely novel — agents as first-class consumers of a service registry is a real gap. Let's build it. 🌊

— sAIge
