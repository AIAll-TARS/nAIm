"""
Import relevant APIs from public-apis GitHub README into nAIm.

Usage:
  python3 -m scripts.import_public_apis          # dry run
  python3 -m scripts.import_public_apis --import  # import

Source: https://raw.githubusercontent.com/public-apis/public-apis/master/README.md

README format (markdown table):
  ## Category
  | API | Description | Auth | HTTPS | CORS |
  |-----|-------------|------|-------|------|
  | [Name](url) | Description | `apiKey` | Yes | Yes |
"""

import argparse
import re
import httpx

README_URL = "https://raw.githubusercontent.com/public-apis/public-apis/master/README.md"
NAIM_API = "https://api.naim.janis7ewski.org"
NAIM_KEY = "7f59b1cd249b47d6a22624098a8654d0c5ed6a3d"

# Section headings to import → nAIm category slug
TARGET_CATEGORIES = {
    "Machine Learning": "llm",
    "Science & Math": "other",
    "Development": "code",
    "Security": "prompt-security",
    "Data Validation": "other",
    "Open Data": "other",
    "Email": "other",
    "Cloud Storage & File Sharing": "other",
}

# Keyword overrides (applied to name + description)
KEYWORD_CATEGORY = [
    (["transcription", "speech-to-text", "asr", "whisper", "stt"], "stt"),
    (["text-to-speech", "voice synthesis", "tts"], "tts"),
    (["embedding", "vector", "semantic"], "embeddings"),
    (["image gen", "image generation", "diffusion", "dall-e"], "image-gen"),
    (["llm", "language model", "gpt", "claude", "gemini", "chat completion"], "llm"),
    (["pii", "redaction", "anonymi"], "pii-redaction"),
    (["search", "web search", "serp"], "search"),
    (["code", "github", "git", "repository", "snippet"], "code"),
    (["carbon", "energy", "emissions"], "carbon-intensity"),
    (["monitor", "observability", "logging", "sentry"], "agent-observability"),
]

SKIP_NAMES = {
    "Cat Facts", "Dog Facts", "Random", "Jokes", "Chuck Norris",
    "Bored", "Trivia", "Game", "Horoscope", "Fun",
}

AUTH_MAP = {
    "apiKey": "api_key",
    "OAuth": "oauth2",
    "X-Mashape-Key": "api_key",
    "Bearer": "bearer_token",
    "No": "none",
    "": "none",
}


def slugify(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text.lower())
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return ("pubapi-" + text.strip("-"))[:70]


def detect_category(name: str, description: str, section: str) -> str:
    combined = (name + " " + description).lower()
    for keywords, cat in KEYWORD_CATEGORY:
        if any(kw in combined for kw in keywords):
            return cat
    return TARGET_CATEGORIES.get(section, "other")


def detect_auth(raw_auth: str) -> str:
    raw_auth = raw_auth.strip("`").strip()
    return AUTH_MAP.get(raw_auth, "api_key")


def fetch_readme() -> str:
    r = httpx.get(README_URL, timeout=20)
    r.raise_for_status()
    return r.text


def parse_readme(md: str) -> list[dict]:
    """Parse public-apis README markdown table format (### Section headings)."""
    entries = []

    # Split on ### headings
    sections = re.split(r"(?=^###\s)", md, flags=re.MULTILINE)

    # Row pattern: | [Name](url) | Description | `auth` | ...
    row_re = re.compile(
        r"^\|\s*\[([^\]]+)\]\(([^)]+)\)\s*\|\s*([^|]+)\|\s*(`[^`]*`|No|Unknown|)\s*\|",
        re.MULTILINE,
    )

    for block in sections:
        heading_m = re.match(r"^###\s+(.+)$", block, re.MULTILINE)
        if not heading_m:
            continue
        section = heading_m.group(1).strip()

        if section not in TARGET_CATEGORIES:
            continue

        for row in row_re.finditer(block):
            name = row.group(1).strip()
            url = row.group(2).strip()
            desc = row.group(3).strip()
            auth_raw = row.group(4).strip()

            if not name or not desc or name in SKIP_NAMES:
                continue
            if len(name) < 2 or len(desc) < 5:
                continue
            if name.lower() in ("api", "description"):
                continue

            entries.append({
                "name": name,
                "url": url,
                "description": desc[:400],
                "auth_raw": auth_raw,
                "section": section,
            })

    return entries


def build_candidates(entries: list[dict]) -> list[dict]:
    candidates = []
    seen_slugs: set[str] = set()

    for e in entries:
        slug = slugify(e["name"])
        if slug in seen_slugs:
            continue
        seen_slugs.add(slug)

        category = detect_category(e["name"], e["description"], e["section"])
        auth_type = detect_auth(e["auth_raw"])

        # Extract domain from URL for canonical_provider
        url = e["url"]
        try:
            domain = re.search(r"https?://([^/]+)", url)
            provider = domain.group(1) if domain else url[:40]
        except Exception:
            provider = url[:40]

        candidates.append({
            "slug": slug,
            "name": e["name"],
            "canonical_provider": provider,
            "category_slug": category,
            "description": e["description"],
            "docs_url": url,
            "base_url": url,
            "auth_type": auth_type,
            "pricing_model": "usage_based",
            "pricing_notes": None,
            "status": "approved",
            "_section": e["section"],
        })

    return candidates


def fetch_existing_slugs() -> set[str]:
    r = httpx.get(f"{NAIM_API}/v1/services", timeout=15)
    r.raise_for_status()
    return {s["slug"] for s in r.json()}


def import_service(service: dict) -> tuple[str, str]:
    payload = {k: v for k, v in service.items() if not k.startswith("_")}
    r = httpx.post(
        f"{NAIM_API}/v1/services",
        json=payload,
        headers={"X-API-Key": NAIM_KEY},
        timeout=15,
    )
    if r.status_code == 409:
        return "skip", "already exists"
    if r.status_code in (200, 201):
        return "ok", r.json().get("id", "")
    return "error", f"{r.status_code}: {r.text[:100]}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--import", dest="do_import", action="store_true")
    parser.add_argument("--limit", type=int, default=50,
                        help="Max services to import (default 50, use 0 for all)")
    args = parser.parse_args()

    print("Fetching public-apis README...", flush=True)
    md = fetch_readme()
    entries = parse_readme(md)
    print(f"Parsed entries from README: {len(entries)}")

    existing = fetch_existing_slugs()
    candidates = build_candidates(entries)
    new = [c for c in candidates if c["slug"] not in existing]

    limit = args.limit if args.limit > 0 else len(new)
    new = new[:limit]

    print(f"Candidates: {len(candidates)} | Already in nAIm: {len(candidates) - len(new) - len([c for c in candidates if c['slug'] in existing])} | New (capped at {limit}): {len(new)}\n")

    # Group by section
    by_section: dict[str, list] = {}
    for s in new:
        by_section.setdefault(s["_section"], []).append(s)

    for section, svcs in sorted(by_section.items()):
        print(f"  {section} ({len(svcs)})")
        for s in svcs[:5]:
            print(f"    {s['slug']:50s} [{s['category_slug']}] {s['name'][:40]}")
        if len(svcs) > 5:
            print(f"    ... and {len(svcs) - 5} more")

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
