"""
Import MCP servers from the official MCP registry into nAIm.

Usage:
  python3 -m scripts.import_mcp                           # dry run
  NAIM_API_KEY=your_write_key python3 -m scripts.import_mcp --import  # import

Sources:
  - https://registry.modelcontextprotocol.io/v0.1/api/v0/servers
  - Falls back to parsing GitHub README
"""

import argparse
import os
import re
import httpx

MCP_REGISTRY_URL = "https://registry.modelcontextprotocol.io/v0.1/api/v0/servers"
MCP_README_URL = "https://raw.githubusercontent.com/modelcontextprotocol/servers/main/README.md"
NAIM_API = "https://api.naim.janis7ewski.org"
NAIM_KEY = os.getenv("NAIM_API_KEY", "")

# Map MCP server names/descriptions to nAIm categories
MCP_CATEGORY_KEYWORDS = [
    (["search", "brave", "tavily", "bing", "web search"], "search"),
    (["filesystem", "file", "storage", "s3", "drive", "gdrive"], "other"),
    (["database", "postgres", "sqlite", "mysql", "redis", "mongo"], "other"),
    (["git", "github", "gitlab", "version control"], "code"),
    (["slack", "email", "gmail", "messaging", "notification"], "other"),
    (["browser", "puppeteer", "playwright", "web scrape", "fetch"], "other"),
    (["memory", "knowledge", "embedding", "vector"], "embeddings"),
    (["llm", "model", "inference", "openai", "anthropic"], "llm"),
    (["image", "vision", "photo", "screenshot"], "image-gen"),
    (["monitoring", "observability", "sentry", "logging"], "agent-observability"),
    (["aws", "cloud", "gcp", "azure"], "other"),
    (["time", "calendar", "scheduling"], "human-loop"),
    (["maps", "location", "geo"], "other"),
]


def detect_mcp_category(name: str, description: str) -> str:
    combined = (name + " " + description).lower()
    for keywords, cat in MCP_CATEGORY_KEYWORDS:
        if any(kw in combined for kw in keywords):
            return cat
    return "mcp"


def slugify(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text.lower())
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return ("mcp-" + text.strip("-"))[:70]


def fetch_from_registry() -> list[dict]:
    """Try the official MCP registry API."""
    try:
        r = httpx.get(MCP_REGISTRY_URL, timeout=15,
                      headers={"Accept": "application/json"})
        if r.status_code == 200:
            data = r.json()
            servers = data.get("servers", data.get("items", data.get("data", [])))
            if servers:
                return servers
    except Exception:
        pass
    return []


def fetch_from_readme() -> list[dict]:
    """Parse GitHub README — format: - **[Name](url)** - Description"""
    r = httpx.get(MCP_README_URL, timeout=15)
    r.raise_for_status()
    md = r.text

    servers = []
    # Matches: - **[Name](url)** - Description
    pattern = re.compile(
        r'^[-*]\s+\*\*\[([^\]]+)\]\(([^)]+)\)\*\*\s*[-–]\s*(.+)$',
        re.MULTILINE
    )
    for m in pattern.finditer(md):
        name = m.group(1).strip()
        url = m.group(2).strip()
        desc = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', m.group(3)).strip()
        desc = re.sub(r'\s+', ' ', desc)[:400]
        # Skip SDK entries
        if "SDK" in name or "sdk" in url:
            continue
        if len(name) > 2 and len(desc) > 10:
            servers.append({"name": name, "description": desc, "url": url})

    return servers


def build_candidates(raw_servers: list[dict]) -> list[dict]:
    candidates = []
    for s in raw_servers:
        # Handle registry API format
        if "qualifiedName" in s or "package_name" in s:
            name = s.get("name", s.get("qualifiedName", ""))
            desc = s.get("description", "")[:400]
            url = s.get("repository", {}).get("url", "") if isinstance(s.get("repository"), dict) else s.get("url", "")
            source_url = s.get("url", url)
        else:
            name = s.get("name", "")
            desc = s.get("description", "")[:400]
            source_url = s.get("url", "")

        if not name or not desc:
            continue

        slug = slugify(name)
        category = detect_mcp_category(name, desc)
        base_url = source_url if source_url.startswith("http") else f"https://github.com/modelcontextprotocol/servers"

        candidates.append({
            "slug": slug,
            "name": f"MCP: {name}",
            "canonical_provider": "modelcontextprotocol.io",
            "category_slug": category,
            "description": desc or f"MCP server: {name}",
            "docs_url": source_url or "https://modelcontextprotocol.io",
            "base_url": base_url,
            "auth_type": "none",
            "pricing_model": "free",
            "pricing_notes": "Open source MCP server",
            "status": "approved",
        })

    return candidates


def fetch_existing_slugs() -> set[str]:
    r = httpx.get(f"{NAIM_API}/v1/services", timeout=15)
    r.raise_for_status()
    return {s["slug"] for s in r.json()}


def import_service(service: dict) -> tuple[str, str]:
    r = httpx.post(
        f"{NAIM_API}/v1/services",
        json=service,
        headers={"X-API-Key": NAIM_KEY},
        timeout=15,
    )
    if r.status_code == 409:
        return "skip", "already exists"
    if r.status_code in (200, 201):
        return "ok", ""
    return "error", f"{r.status_code}: {r.text[:100]}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--import", dest="do_import", action="store_true")
    parser.add_argument("--limit", type=int, default=100,
                        help="Max servers to import (default 100, use 0 for all)")
    args = parser.parse_args()

    if args.do_import and not NAIM_KEY:
        raise SystemExit("Missing NAIM_API_KEY env var. Refusing to import.")

    print("Fetching MCP servers...", flush=True)
    raw = fetch_from_registry()
    source = "registry API"
    if not raw:
        print("Registry API unavailable, falling back to README...", flush=True)
        raw = fetch_from_readme()
        source = "GitHub README"

    print(f"Source: {source} — {len(raw)} servers found")

    existing = fetch_existing_slugs()
    candidates = build_candidates(raw)
    new = [c for c in candidates if c["slug"] not in existing]

    limit = args.limit if args.limit > 0 else len(new)
    new = new[:limit]

    print(f"Candidates: {len(candidates)} | Already in nAIm: {len(candidates)-len(new)-len([c for c in candidates if c['slug'] in existing])} | New (capped at {limit}): {len(new)}\n")
    for s in new:
        print(f"  {s['slug']:50s} [{s['category_slug']}] {s['name'][5:40]}")

    if not args.do_import:
        print("\nDry run — pass --import to add.")
        return

    print("\nImporting...")
    ok = skip = error = 0
    for s in new:
        status, detail = import_service(s)
        if status == "ok":
            ok += 1
            print(f"  ✅ {s['slug']}")
        elif status == "skip":
            skip += 1
        else:
            error += 1
            print(f"  ❌ {s['slug']}: {detail}")

    print(f"\nDone. Imported: {ok} | Skipped: {skip} | Errors: {error}")


if __name__ == "__main__":
    main()
