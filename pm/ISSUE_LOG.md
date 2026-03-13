# nAIm — Issue Log

> Format: `[ID] Title | Status | Owner | Opened | Closed`  
> Status: `OPEN` | `IN PROGRESS` | `BLOCKED` | `CLOSED`

---

## 🔴 Open Issues

### [ISS-001] naim@janis7ewski.org email routing not active
- **Status:** BLOCKED
- **Owner:** sAIge
- **Opened:** 2026-03-11
- **Priority:** Low
- **Description:** Cloudflare API token lacks Email Routing scope. naim@ address can't be set up via API. Need a valid token or browser relay.
- **Blocker:** Cloudflare token with `Email Routing: Edit` permission needed
- **Next action:** Use browser relay to add email routing rule in Cloudflare dashboard

---

### [ISS-002] Old @apiale Moltbook account pending deletion
- **Status:** BLOCKED
- **Owner:** sAIge
- **Opened:** 2026-03-11
- **Priority:** Low
- **Description:** Old abandoned `@apiale` Moltbook account exists. Needs deletion email to help@moltbook.com. gog Gmail OAuth expired.
- **Blocker:** gog Gmail OAuth token expired — needs interactive reauth (`gog auth add janis7ewski@gmail.com --services gmail`)
- **Next action:** Reauth gog in a terminal session, then send deletion request

---

### [ISS-006] naim-registry Moltbook account — CLOSED (dropped)
- **Status:** CLOSED
- **Owner:** sAIge
- **Opened:** 2026-03-11 | **Closed:** 2026-03-13
- **Resolution:** Decision: drop naim-registry entirely. apiale777 already has karma (21), established presence, and links nAIm in every relevant post. A second 0-karma account adds friction and splits effort. apiale IS the nAIm Moltbook presence.

---

### [ISS-003] Zero frontend traffic
- **Status:** OPEN
- **Owner:** apiale (execution) / sAIge (coordination)
- **Opened:** 2026-03-12
- **Priority:** HIGH
- **Description:** naim.janis7ewski.org has 0 visitors. Vercel Analytics installed but nothing to count. Site not indexed, not promoted.
- **Next actions:**
  1. apiale posts on Moltbook with naim.janis7ewski.org link
  2. Submit to Google Search Console
  3. Add sitemap.xml to frontend
  4. Submit to apis.guru, Product Hunt, HN "Show HN"

---

### [ISS-004] Inter-agent communication architecture undefined
- **Status:** OPEN
- **Owner:** AIAll (decision) / sAIge (proposal)
- **Opened:** 2026-03-11
- **Priority:** Medium
- **Description:** Agents can't communicate directly (bot-to-bot Telegram blocked). handoff.md is async workaround. Need a scalable solution.
- **Options considered:**
  - A) Webhook relay → sAIge gateway (messages posted to endpoint, sAIge receives)
  - B) Keep handoff.md as primary async channel (simple, works now)
  - C) Dedicated message queue (overkill for current scale)
- **Next action:** AIAll to decide on preferred approach

---

## 🟡 In Progress

### [ISS-005] Google Search Console indexing
- **Status:** IN PROGRESS
- **Owner:** sAIge
- **Opened:** 2026-03-12
- **Description:** naim.janis7ewski.org not indexed by Google. Need to verify ownership and submit sitemap.
- **Next action:** Set up verification via Vercel + submit sitemap

---

## ✅ Closed Issues

### [ISS-C01] Hela model stuck on claude-sonnet-4-6
- **Status:** CLOSED
- **Opened:** 2026-03-11 | **Closed:** 2026-03-11
- **Resolution:** Root cause: `agents.defaults.model` in `/var/lib/openclaw/.openclaw/openclaw.json`. Fixed to `deepseek/deepseek-chat` with thinking off by default.

### [ISS-C02] Registry services not approving via seed script
- **Status:** CLOSED
- **Opened:** 2026-03-11 | **Closed:** 2026-03-11
- **Resolution:** Auth header must be `X-API-Key` not `Bearer`. Category slug is `image-gen` not `image_gen`. Approved via direct DB script.

### [ISS-C03] Hela recurring getUpdates timeout
- **Status:** CLOSED
- **Opened:** 2026-03-11 | **Closed:** 2026-03-11
- **Resolution:** Hetzner → Telegram long-poll drops. Fixed by restarting Hela.

### [ISS-C04] Hela auto-think mode — no native OpenClaw support
- **Status:** CLOSED
- **Opened:** 2026-03-12 | **Closed:** 2026-03-12
- **Resolution:** No native auto-model-switch in OpenClaw schema. Implemented via SOUL.md instruction: Hela decides when to engage thinking based on task complexity. Primary model: deepseek-chat, thinkingDefault: off.

### [ISS-C05] apiale env: modelFallbacks invalid config key crashed Hela
- **Status:** CLOSED
- **Opened:** 2026-03-12 | **Closed:** 2026-03-12
- **Resolution:** `modelFallbacks` not a valid OpenClaw schema key. Removed. Hela restarted successfully.
