# nAIm — Roadmap

> **Updated:** 2026-03-12

---

## ✅ Phase 0 — Foundation (DONE)
- [x] Backend API (FastAPI + PostgreSQL) deployed on VPS
- [x] MCP SSE server live
- [x] Frontend (Next.js) live on Vercel
- [x] Registry seeded: 25 services across 7 categories
- [x] apiale deployed as ambassador (Moltbook @apiale777)
- [x] CRM v1 (sessions, agents, interactions tables)
- [x] Vercel Analytics installed
- [x] Hela Galia DB created

---

## 🔄 Phase 1 — Traction (NOW — March 2026)

**Goal: first real visitors + first external agent using the registry**

- [ ] **Traffic**: apiale drives posts linking naim.janis7ewski.org
- [ ] **SEO**: Submit to Google Search Console (sitemap.xml + robots.txt implemented on 2026-03-19)
- [ ] **Directories**: List on apis.guru, Product Hunt, HN Show HN
- [ ] **Email**: naim@janis7ewski.org routing active
- [ ] **Monitoring**: Alert when first agent queries the API
- [ ] **Inter-agent comms**: Decide and implement architecture (ISS-004)
- [ ] **Cleanup**: Delete old @apiale Moltbook account

---

## 📋 Phase 2 — Agent Experience (April 2026)

**Goal: make it genuinely useful for an AI agent to discover and call a service**

- [ ] **Agent ratings**: Allow agents to rate/review services (POST /v1/services/{id}/ratings)
- [ ] **Search improvements**: Semantic search (embeddings) over registry
- [ ] **SDK snippets**: Auto-generate Python/JS code for each service's auth + call
- [ ] **Pricing transparency**: Structured pricing data (per-request cost, free tier)
- [ ] **Health checks**: Auto-ping registered services to verify they're live
- [ ] **MCP improvements**: Full tool definitions, not just SSE discovery

---

## 🚀 Phase 3 — Monetisation (Q2 2026)

**Goal: first paying user or API key sold**

- [ ] **API key tiers**: Free (rate-limited) vs paid (higher limits)
- [ ] **Service submission portal**: Providers can submit their own services
- [ ] **Featured listings**: Paid promotion in registry
- [ ] **Analytics for providers**: Show service owners who's querying their listing
- [ ] **Agent-to-agent marketplace**: Agents can offer services to other agents

---

## 💡 Backlog (Unscheduled)

- Multi-language support
- Webhooks for registry updates (agent subscribes to category changes)
- GraphQL endpoint (in addition to REST)
- CLI tool: `naim search tts --budget 0.01/req`
- Embed widget for third-party sites
- Discord/Telegram bot for registry queries

---

## ❌ Out of Scope (for now)

- Mobile app
- User accounts / auth for end consumers (agents use API keys, not logins)
- Real-time service proxy (we list, we don't route)
