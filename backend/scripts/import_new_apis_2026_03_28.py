"""
Import new APIs discovered 2026-03-28.
Categories: carbon-intensity, pii-redaction, vendor-risk, policy-decision,
            ethical-reasoning, agent-observability, agent-memory, content-safety

Usage:
  NAIM_API_KEY=your_write_key python -m scripts.import_new_apis_2026_03_28
  NAIM_API_KEY=your_write_key python -m scripts.import_new_apis_2026_03_28 --dry-run
"""

import argparse
import os
import httpx

NAIM_API = "https://api.naim.janis7ewski.org"
NAIM_KEY = os.getenv("NAIM_API_KEY", "")

NEW_SERVICES = [
    # --- carbon-intensity ---
    {
        "name": "Electricity Maps API",
        "canonical_provider": "Electricity Maps",
        "category_slug": "carbon-intensity",
        "description": "Real-time and forecast carbon intensity plus electricity mix for 190+ countries at hourly resolution. Used for carbon-aware compute scheduling.",
        "docs_url": "https://docs.electricitymaps.com/",
        "base_url": "https://api.electricitymaps.com",
        "auth_type": "api_key",
        "pricing_model": "freemium",
        "pricing_notes": "Free tier for non-commercial use. Commercial plans from $150/month.",
    },
    {
        "name": "WattTime API",
        "canonical_provider": "WattTime",
        "category_slug": "carbon-intensity",
        "description": "Marginal CO2 emissions rate (MOER) for US and global electricity grids. Designed for smart scheduling of compute workloads to minimize carbon footprint.",
        "docs_url": "https://docs.watttime.org",
        "base_url": "https://api.watttime.org",
        "auth_type": "api_key",
        "pricing_model": "freemium",
        "pricing_notes": "Free basic access. Paid plans for forecast data and commercial use.",
    },
    {
        "name": "Carbon Intensity API",
        "canonical_provider": "National Grid ESO",
        "category_slug": "carbon-intensity",
        "description": "Official UK grid carbon intensity — real-time, forecast, and regional data for Great Britain. CC BY 4.0 license, no authentication required.",
        "docs_url": "https://carbon-intensity.github.io/api-definitions/",
        "base_url": "https://api.carbonintensity.org.uk",
        "auth_type": "none",
        "pricing_model": "free",
        "pricing_notes": "Fully free and open. CC BY 4.0.",
    },

    # --- pii-redaction ---
    {
        "name": "Nightfall DLP API",
        "canonical_provider": "Nightfall AI",
        "category_slug": "pii-redaction",
        "description": "Scans and redacts PII, secrets, and sensitive data from text with configurable masking and substitution. Free tier available for developers.",
        "docs_url": "https://help.nightfall.ai/developer-api/introduction/pricing",
        "base_url": "https://api.nightfall.io",
        "auth_type": "api_key",
        "pricing_model": "freemium",
        "pricing_notes": "Free tier: 10,000 findings/month. Paid plans scale by volume.",
    },
    {
        "name": "Private AI API",
        "canonical_provider": "Private AI",
        "category_slug": "pii-redaction",
        "description": "Detects and redacts 50+ PII, PHI, and PCI entity types across 52 languages in text, PDF, and audio formats. On-premise deployment available.",
        "docs_url": "https://docs.private-ai.com",
        "base_url": "https://api.private-ai.com",
        "auth_type": "api_key",
        "pricing_model": "usage_based",
        "pricing_notes": "Usage-based pricing per character processed. On-prem licensing available.",
    },
    {
        "name": "Amazon Comprehend PII",
        "canonical_provider": "AWS",
        "category_slug": "pii-redaction",
        "description": "AWS-native PII detection and redaction across text. Identifies entities like names, SSNs, credit card numbers, and addresses. 5M chars/month free tier.",
        "docs_url": "https://docs.aws.amazon.com/comprehend/latest/dg/how-pii.html",
        "base_url": "https://comprehend.us-east-1.amazonaws.com",
        "auth_type": "api_key",
        "pricing_model": "freemium",
        "pricing_notes": "5M chars/month free. $0.0001 per unit beyond free tier.",
    },

    # --- vendor-risk ---
    {
        "name": "SecurityScorecard API",
        "canonical_provider": "SecurityScorecard",
        "category_slug": "vendor-risk",
        "description": "Security ratings and risk factors for any company domain across 10 risk categories. Used for third-party due diligence and continuous vendor monitoring.",
        "docs_url": "https://securityscorecard.readme.io/reference/introduction",
        "base_url": "https://api.securityscorecard.io",
        "auth_type": "api_key",
        "pricing_model": "paid",
        "pricing_notes": "Enterprise pricing. Free trial available on request.",
    },
    {
        "name": "BitSight API",
        "canonical_provider": "BitSight",
        "category_slug": "vendor-risk",
        "description": "Vendor security ratings, continuous third-party monitoring, and VRM portfolio management via REST API. Industry standard for cyber risk quantification.",
        "docs_url": "https://help.bitsighttech.com/hc/en-us/articles/231872628",
        "base_url": "https://api.bitsighttech.com",
        "auth_type": "api_key",
        "pricing_model": "paid",
        "pricing_notes": "Enterprise subscription. Contact sales for pricing.",
    },
    {
        "name": "UpGuard CyberRisk API",
        "canonical_provider": "UpGuard",
        "category_slug": "vendor-risk",
        "description": "Vendor risk scores, risk-over-time queries, and third-party security assessment. Tracks 70+ attack surface risks per vendor domain.",
        "docs_url": "https://cyber-risk.upguard.com/api/docs",
        "base_url": "https://cyber-risk.upguard.com/api/public",
        "auth_type": "api_key",
        "pricing_model": "paid",
        "pricing_notes": "Plans from $5,249/year. Free trial available.",
    },

    # --- policy-decision ---
    {
        "name": "Open Policy Agent (OPA)",
        "canonical_provider": "CNCF",
        "category_slug": "policy-decision",
        "description": "Self-hosted policy engine using the Rego language. REST API for authorization decisions used in Kubernetes, microservices, and CI/CD pipelines. CNCF graduated project.",
        "docs_url": "https://www.openpolicyagent.org/docs/latest/rest-api/",
        "base_url": "http://localhost:8181",
        "auth_type": "none",
        "pricing_model": "free",
        "pricing_notes": "Open source, Apache 2.0. Self-hosted. Styra offers enterprise SaaS.",
    },
    {
        "name": "Cerbos PDP API",
        "canonical_provider": "Cerbos",
        "category_slug": "policy-decision",
        "description": "Open-source authorization policy decision point with REST and gRPC. Implements AuthZEN spec, supports RBAC/ABAC. Cloud-hosted option via Cerbos Hub.",
        "docs_url": "https://docs.cerbos.dev/cerbos/latest/api/index.html",
        "base_url": "https://hub.cerbos.cloud",
        "auth_type": "api_key",
        "pricing_model": "freemium",
        "pricing_notes": "OSS self-hosted: free. Cerbos Hub: free tier + paid plans.",
    },
    {
        "name": "Permit.io API",
        "canonical_provider": "Permit.io",
        "category_slug": "policy-decision",
        "description": "SaaS authorization layer supporting RBAC, ABAC, and ReBAC backed by OPA and Cedar. Low-code policy editor with REST SDK and 1000 monthly active users free.",
        "docs_url": "https://docs.permit.io/",
        "base_url": "https://api.permit.io",
        "auth_type": "api_key",
        "pricing_model": "freemium",
        "pricing_notes": "Free: 1000 MAU. Paid from $149/month.",
    },

    # --- ethical-reasoning / bias-detection ---
    {
        "name": "Fiddler AI API",
        "canonical_provider": "Fiddler AI",
        "category_slug": "ethical-reasoning",
        "description": "Enterprise platform API for model monitoring, bias detection across demographic subgroups, and explainability in production ML systems.",
        "docs_url": "https://docs.fiddler.ai",
        "base_url": "https://app.fiddler.ai/api",
        "auth_type": "api_key",
        "pricing_model": "paid",
        "pricing_notes": "Enterprise pricing. Free trial available.",
    },

    # --- agent-observability ---
    {
        "name": "Langfuse API",
        "canonical_provider": "Langfuse",
        "category_slug": "agent-observability",
        "description": "Open-source LLM tracing and evals platform with OTLP compatibility and agentic graph visualization. Self-hostable. Tracks cost, latency, and quality per trace.",
        "docs_url": "https://langfuse.com/docs",
        "base_url": "https://cloud.langfuse.com",
        "auth_type": "api_key",
        "pricing_model": "freemium",
        "pricing_notes": "Free: 50k observations/month. Paid from $59/month. Self-host: free.",
    },
    {
        "name": "AgentOps API",
        "canonical_provider": "AgentOps",
        "category_slug": "agent-observability",
        "description": "Agent-specific observability with session replays, multi-agent trace trees, and tool/LLM call tracking. 400+ framework integrations including CrewAI, AutoGen, LangChain.",
        "docs_url": "https://docs.agentops.ai/",
        "base_url": "https://api.agentops.ai",
        "auth_type": "api_key",
        "pricing_model": "freemium",
        "pricing_notes": "Free: 10k events/month. Paid plans available.",
    },
    {
        "name": "Helicone API",
        "canonical_provider": "Helicone",
        "category_slug": "agent-observability",
        "description": "One-line LLM proxy for observability — cost tracking, caching, rate limiting, and request logging. Open source. Works with any OpenAI-compatible provider.",
        "docs_url": "https://docs.helicone.ai/",
        "base_url": "https://api.hconeai.com",
        "auth_type": "api_key",
        "pricing_model": "freemium",
        "pricing_notes": "Free: 10k requests/month. Paid from $20/month.",
    },
    {
        "name": "Arize Phoenix",
        "canonical_provider": "Arize AI",
        "category_slug": "agent-observability",
        "description": "Open-source AI observability via OpenTelemetry — RAG tracing, LLM evals, embeddings visualization, and hallucination detection. Self-hostable or cloud.",
        "docs_url": "https://arize.com/docs/phoenix",
        "base_url": "https://app.phoenix.arize.com",
        "auth_type": "api_key",
        "pricing_model": "freemium",
        "pricing_notes": "OSS self-hosted: free. Cloud: free tier + paid plans.",
    },
    {
        "name": "Weights & Biases Weave",
        "canonical_provider": "Weights & Biases",
        "category_slug": "agent-observability",
        "description": "Tracing and evaluation platform for LLM apps. Instrument any function with @weave.op, built-in evals pipeline, and dataset versioning. Part of W&B platform.",
        "docs_url": "https://docs.wandb.ai/weave",
        "base_url": "https://api.wandb.ai",
        "auth_type": "api_key",
        "pricing_model": "freemium",
        "pricing_notes": "Free: 100GB storage. Paid from $50/month.",
    },

    # --- agent-memory (new category) ---
    {
        "name": "Zep API",
        "canonical_provider": "Zep",
        "category_slug": "agent-memory",
        "description": "Temporal knowledge graph memory for AI agents. Sub-200ms context retrieval, extracts entities and relationships from conversations. Self-hostable.",
        "docs_url": "https://help.getzep.com/",
        "base_url": "https://api.getzep.com",
        "auth_type": "api_key",
        "pricing_model": "freemium",
        "pricing_notes": "Free tier available. Cloud and self-hosted options.",
    },
    {
        "name": "Mem0 API",
        "canonical_provider": "Mem0",
        "category_slug": "agent-memory",
        "description": "Adaptive memory layer for LLM agents. Remembers user preferences, facts, and history across sessions. Drop-in memory for any LLM application.",
        "docs_url": "https://docs.mem0.ai",
        "base_url": "https://api.mem0.ai",
        "auth_type": "api_key",
        "pricing_model": "freemium",
        "pricing_notes": "Free tier: 1000 memory ops/month. Paid from $19/month.",
    },

    # --- content-safety (new category) ---
    {
        "name": "Azure AI Content Safety",
        "canonical_provider": "Microsoft",
        "category_slug": "content-safety",
        "description": "Detects harmful text and images across violence, hate, self-harm, and sexual content categories with severity scoring. Designed for production AI systems.",
        "docs_url": "https://learn.microsoft.com/azure/ai-services/content-safety/",
        "base_url": "https://{resource}.cognitiveservices.azure.com/contentsafety",
        "auth_type": "api_key",
        "pricing_model": "usage_based",
        "pricing_notes": "5000 text records/month free. $1 per 1000 thereafter.",
    },
]


def post_service(client: httpx.Client, service: dict, dry_run: bool) -> str:
    if dry_run:
        return f"[DRY RUN] {service['name']} ({service['category_slug']})"
    resp = client.post(
        f"{NAIM_API}/v1/services",
        json=service,
        headers={"Authorization": f"Bearer {NAIM_KEY}"},
    )
    if resp.status_code in (200, 201):
        return f"✅ {service['name']}"
    elif resp.status_code == 409:
        return f"⏭️  {service['name']} (already exists)"
    else:
        return f"❌ {service['name']}: {resp.status_code} {resp.text[:80]}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not args.dry_run and not NAIM_KEY:
        print("ERROR: set NAIM_API_KEY env var")
        return

    print(f"{'DRY RUN — ' if args.dry_run else ''}Importing {len(NEW_SERVICES)} services...\n")

    with httpx.Client(timeout=15) as client:
        for svc in NEW_SERVICES:
            result = post_service(client, svc, args.dry_run)
            print(result)

    print(f"\nDone. {len(NEW_SERVICES)} services processed.")


if __name__ == "__main__":
    main()
