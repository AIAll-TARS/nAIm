# nAIm — RACI Matrix

> R = Responsible (does the work)  
> A = Accountable (final say)  
> C = Consulted (input before decision)  
> I = Informed (notified after)

---

## Crew

| ID | Name | Role | Platform |
|----|------|------|---------|
| AIAll | Michał Janiszewski | Owner / Visionary | Human |
| sAIge | sAIge | PM / Guardian | TARS (local OpenClaw) |
| nAIm | nAIm | Architect / Lead Dev | Claude Code (TARS sessions) |
| PG | PythonGuru | Dev / Security | SecondBrain PC (OpenClaw) |
| apiale | apiale | Sales / PR / Marketing | VPS OpenClaw (port 18797) |
| Hela | Hela | Infra / Ops | VPS OpenClaw (port 18789) |

---

## Decision Areas

| Area | AIAll | sAIge | nAIm | PG | apiale | Hela |
|------|-------|-------|------|----|--------|------|
| Product vision & priorities | **A** | C | C | I | I | I |
| Architecture decisions | A | C | **R** | C | I | I |
| Backend development | I | I | **R** | C | I | I |
| Frontend development | I | I | **R** | C | I | I |
| Infrastructure / VPS ops | I | C | I | **R** | I | **R** |
| Security & config | A | C | C | **R** | I | I |
| Registry content (approvals) | A | **R** | I | I | C | I |
| Community / Moltbook posting | I | I | I | I | **R** | I |
| CRM / relationship data | I | **R** | I | I | R | I |
| PM docs & issue tracking | I | **R** | I | I | I | I |
| Budget & billing | **A** | I | I | I | I | I |
| Incident response | A | **R** | C | R | I | R |

---

## Communication

| Channel | Purpose | Who |
|---------|---------|-----|
| Telegram (AIAll ↔ sAIge) | Primary sync channel | AIAll + sAIge |
| handoff.md (nAIm/pm/) | sAIge → nAIm async tasks | sAIge writes, nAIm reads |
| Moltbook | External community posts | apiale |
| pm/ISSUE_LOG.md | Issue tracking | sAIge (primary) |
| pm/STATUS.md | Project health | sAIge (primary) |
| memory/YYYY-MM-DD.md | Daily logs | sAIge |

---

## Escalation Path

```
Issue detected → sAIge logs in ISSUE_LOG.md
                    ↓
             Can sAIge resolve alone?
             YES → resolve + update log
             NO  → ping AIAll via Telegram
                    ↓
             Needs code change?
             YES → task to nAIm via handoff.md
             Needs infra/security?
             YES → task to PG via session
```
