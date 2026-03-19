"""
Import relevant APIs from apis.guru into the nAIm registry.

Usage:
  # Dry run — show what would be imported:
  python -m scripts.import_apis_guru

  # Actually import (requires NAIM_API_KEY env var):
  NAIM_API_KEY=your_write_key python -m scripts.import_apis_guru --import

  # Import specific category only:
  python -m scripts.import_apis_guru --import --filter machine_learning

apis.guru API: https://api.apis.guru/v2/list.json
"""

import argparse
import hashlib
import os
import re
import sys
import httpx

APIS_GURU_URL = "https://api.apis.guru/v2/list.json"
NAIM_API = "https://api.naim.janis7ewski.org"
NAIM_KEY = os.getenv("NAIM_API_KEY", "")

# apis.guru category → nAIm category slug
CATEGORY_MAP = {
    "machine_learning": "llm",       # overridden per-service below
    "text": "other",                  # overridden per-service below
    "search": "search",
    "security": "prompt-security",
    "monitoring": "agent-observability",
}

# Keyword → nAIm category (applied to title+description, overrides CATEGORY_MAP)
KEYWORD_CATEGORY = [
    (["transcription", "stt", "speech-to-text", "asr", "whisper", "speech-to-text", "asynchronous speech"], "stt"),
    (["text-to-speech", "voice synthesis", " tts "], "tts"),
    (["embedding", "vector", "semantic search"], "embeddings"),
    (["image gen", "image generation", "dall-e", "diffusion", "stable diffusion"], "image-gen"),
    (["code", "copilot", "code generation", "coding assistant"], "code"),
    (["pii", "redaction", "anonymi"], "pii-redaction"),
    (["policy", "decision", "opa", "open policy"], "policy-decision"),
    (["provenance", "watermark", "content authenticity"], "provenance"),
    (["carbon", "energy", "emissions", "sustainability"], "carbon-intensity"),
    (["llm", "language model", "gpt", "claude", "gemini", "mistral", "chat completion"], "llm"),
    (["ocr", "document", "pdf", "extract"], "other"),
    (["translation", "translate", "nlp", "natural language"], "other"),
    (["search", "web search", "serp"], "search"),
]

# Skip these — junk, toy, or clearly irrelevant
SKIP_KEYWORDS = [
    "pirate", "shakespeare", "starwars", "braile", "taunt", "riddle",
    "trivia", "fake-identity", "lottery", "namegen", "uuid", "qrcode",
    "barcode", "random", "poemist", "lovecraft", "fun", "game",
    "football", "sport", "weather", "geodata", "deprecated",
]

# Skip these domains entirely
SKIP_DOMAINS = {
    "fungenerators.com", "funtranslations.com", "randomlovecraft.com",
    "poemist.com", "tafqit.herokuapp.com", "calorieninjas.com",
    "exlibrisgroup.com", "testfire.net", "libretranslate.local",
    "conjur.local", "okta.local", "patrowl.local", "seldon.local",
    "1password.local", "salesforce.local", "6-dot-authentiqio.appspot.com",
    "exude-api.herokuapp.com", "libretranslate.local",
    # Enterprise security — not prompt security
    "cisco.com", "1password.com", "ix-api.net", "credas.co.uk",
    "circl.lu", "cycat.org", "n-auth.com", "uscann.net",
    "authentiq.io", "6-dot-authentiqio.appspot.com",
    # Deprecated or low quality
    "rumble.run", "rapidapi.com",
    # Already in nAIm under different slugs
    "elevenlabs.io",
}


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text[:60].strip("-")


def detect_category(title: str, description: str, guru_cats: list[str]) -> str:
    combined = (title + " " + description).lower()
    for keywords, naim_cat in KEYWORD_CATEGORY:
        if any(kw in combined for kw in keywords):
            return naim_cat
    for guru_cat in guru_cats:
        if guru_cat in CATEGORY_MAP:
            return CATEGORY_MAP[guru_cat]
    return "other"


def detect_auth(security_schemes: dict) -> str:
    if not security_schemes:
        return "none"
    for scheme in security_schemes.values():
        t = scheme.get("type", "").lower()
        name = scheme.get("name", "").lower()
        if t == "oauth2":
            return "oauth2"
        if t == "http" and scheme.get("scheme", "").lower() == "bearer":
            return "bearer_token"
        if t == "apikey" or "api" in name or "key" in name:
            return "api_key"
    return "api_key"


def detect_pricing(title: str, description: str) -> str:
    combined = (title + " " + description).lower()
    if any(w in combined for w in ["free", "open source", "open-source", "no charge"]):
        return "free"
    return "usage_based"


def should_skip(domain: str, title: str, description: str) -> bool:
    base_domain = domain.split(":")[0]
    if base_domain in SKIP_DOMAINS:
        return True
    combined = (domain + " " + title + " " + description).lower()
    if any(kw in combined for kw in SKIP_KEYWORDS):
        return True
    return False


def fetch_apis_guru() -> dict:
    print("Fetching apis.guru list...", flush=True)
    r = httpx.get(APIS_GURU_URL, timeout=30)
    r.raise_for_status()
    return r.json()


def fetch_existing_slugs() -> set[str]:
    r = httpx.get(f"{NAIM_API}/v1/services", timeout=15)
    r.raise_for_status()
    return {s["slug"] for s in r.json()}


def fetch_existing_categories() -> set[str]:
    r = httpx.get(f"{NAIM_API}/v1/categories", timeout=15)
    r.raise_for_status()
    return {c["slug"] for c in r.json()}


def build_candidates(raw: dict, filter_cat: str | None = None) -> list[dict]:
    TARGET_CATS = set(CATEGORY_MAP.keys())
    candidates = []

    for domain, api in raw.items():
        preferred = api["preferred"]
        v = api["versions"][preferred]
        info = v["info"]
        guru_cats = info.get("x-apisguru-categories", [])

        if not any(c in TARGET_CATS for c in guru_cats):
            continue

        title = info.get("title", domain)
        description = info.get("description", "")[:400]

        if should_skip(domain, title, description):
            continue

        # Determine servers/base_url
        servers = v.get("swaggerUrl", "")
        # Try to extract base URL from the spec URL pattern
        base_url = f"https://{domain.split(':')[0]}"

        # Contact / docs
        contact = info.get("contact", {})
        docs_url = contact.get("url", "") or v.get("externalDocs", {}).get("url", "") or base_url

        # Auth — peek at security schemes if available
        components = v.get("components", {})
        security_schemes = components.get("securitySchemes", {})
        auth_type = detect_auth(security_schemes)

        naim_cat = detect_category(title, description, guru_cats)

        if filter_cat and naim_cat != filter_cat:
            continue

        # Generate a stable slug from domain
        slug_base = slugify(domain.replace(":", "-").replace(".", "-"))
        slug = slug_base

        pricing = detect_pricing(title, description)

        candidates.append({
            "slug": slug,
            "name": title,
            "canonical_provider": domain.split(":")[0],
            "category_slug": naim_cat,
            "description": description or f"{title} API",
            "docs_url": docs_url,
            "base_url": base_url,
            "auth_type": auth_type,
            "pricing_model": pricing,
            "pricing_notes": None,
            "status": "approved",
            "_guru_cats": guru_cats,
            "_domain": domain,
        })

    return candidates


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
    parser.add_argument("--import", dest="do_import", action="store_true",
                        help="Actually import (default is dry run)")
    parser.add_argument("--filter", dest="filter_cat", default=None,
                        help="Only import services mapping to this nAIm category")
    args = parser.parse_args()

    if args.do_import and not NAIM_KEY:
        raise SystemExit("Missing NAIM_API_KEY env var. Refusing to import.")

    raw = fetch_apis_guru()
    existing_slugs = fetch_existing_slugs()
    existing_cats = fetch_existing_categories()

    candidates = build_candidates(raw, args.filter_cat)
    new = [c for c in candidates if c["slug"] not in existing_slugs]

    print(f"\nTotal apis.guru candidates: {len(candidates)}")
    print(f"Already in nAIm:            {len(candidates) - len(new)}")
    print(f"New to import:              {len(new)}\n")

    # Group by category
    by_cat: dict[str, list] = {}
    for s in new:
        by_cat.setdefault(s["category_slug"], []).append(s)

    for cat, services in sorted(by_cat.items()):
        print(f"  {cat} ({len(services)})")
        for s in services:
            print(f"    {'[NEW CAT]' if cat not in existing_cats else ''} "
                  f"{s['slug']:50s} {s['name'][:50]}")

    if not args.do_import:
        print("\nDry run — pass --import to actually add these services.")
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
