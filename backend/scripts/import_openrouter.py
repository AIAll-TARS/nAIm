"""
Import LLM models from OpenRouter into the nAIm registry.

Usage:
  python3 -m scripts.import_openrouter          # dry run
  python3 -m scripts.import_openrouter --import  # import

Source: https://openrouter.ai/api/v1/models
"""

import argparse
import re
import httpx

OPENROUTER_URL = "https://openrouter.ai/api/v1/models"
NAIM_API = "https://api.naim.janis7ewski.org"
NAIM_KEY = "7f59b1cd249b47d6a22624098a8654d0c5ed6a3d"

# Only import well-known providers — skip obscure/experimental models
ALLOWED_PROVIDERS = {
    "openai", "anthropic", "google", "meta-llama", "mistralai", "cohere",
    "deepseek", "qwen", "microsoft", "amazon", "nvidia", "perplexity",
    "x-ai", "01-ai", "inflection", "databricks", "together", "nousresearch",
}

# Skip models that are just variants/fine-tunes of the same base (keep best per family)
SKIP_PATTERNS = [
    r":free$", r":nitro$", r":extended$", r":floor$",
    r"-beta$", r"-preview$", r"instruct-v\d",
]


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_/]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return ("openrouter-" + text)[:70].strip("-")


def detect_pricing(pricing: dict) -> tuple[str, str | None]:
    prompt = float(pricing.get("prompt", 0))
    completion = float(pricing.get("completion", 0))
    if prompt == 0 and completion == 0:
        return "free", "Free via OpenRouter"
    cost_per_1m = round((prompt + completion) * 500_000, 4)  # avg input+output
    return "usage_based", f"~${cost_per_1m:.4f}/1M tokens (via OpenRouter)"


def fetch_models() -> list[dict]:
    r = httpx.get(OPENROUTER_URL, timeout=20)
    r.raise_for_status()
    return r.json().get("data", [])


def fetch_existing_slugs() -> set[str]:
    r = httpx.get(f"{NAIM_API}/v1/services", timeout=15)
    r.raise_for_status()
    return {s["slug"] for s in r.json()}


def should_skip(model_id: str) -> bool:
    for pat in SKIP_PATTERNS:
        if re.search(pat, model_id):
            return True
    return False


def build_candidates(models: list[dict]) -> list[dict]:
    candidates = []
    seen_families: dict[str, int] = {}  # family -> count, limit per family

    for m in models:
        model_id = m.get("id", "")
        provider = model_id.split("/")[0] if "/" in model_id else ""

        if provider not in ALLOWED_PROVIDERS:
            continue
        if should_skip(model_id):
            continue

        # Limit to 3 models per provider family to avoid flooding
        family = provider
        seen_families[family] = seen_families.get(family, 0) + 1
        if seen_families[family] > 5:
            continue

        name = m.get("name", model_id)
        description = (m.get("description") or "")[:400]
        if not description:
            ctx = m.get("context_length", 0)
            description = f"{name} — LLM via OpenRouter. Context: {ctx:,} tokens."

        pricing_model, pricing_notes = detect_pricing(m.get("pricing", {}))
        slug = slugify(model_id)

        candidates.append({
            "slug": slug,
            "name": name,
            "canonical_provider": f"openrouter.ai ({provider})",
            "category_slug": "llm",
            "description": description,
            "docs_url": f"https://openrouter.ai/{model_id}",
            "base_url": "https://openrouter.ai/api/v1",
            "auth_type": "api_key",
            "pricing_model": pricing_model,
            "pricing_notes": pricing_notes,
            "status": "approved",
            "_model_id": model_id,
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
    parser.add_argument("--import", dest="do_import", action="store_true")
    args = parser.parse_args()

    print("Fetching OpenRouter models...", flush=True)
    models = fetch_models()
    print(f"Total models from OpenRouter: {len(models)}")

    existing = fetch_existing_slugs()
    candidates = build_candidates(models)
    new = [c for c in candidates if c["slug"] not in existing]

    print(f"Filtered candidates: {len(candidates)}")
    print(f"Already in nAIm: {len(candidates) - len(new)}")
    print(f"New to import: {len(new)}\n")

    # Group by provider
    by_provider: dict[str, list] = {}
    for s in new:
        p = s["_model_id"].split("/")[0]
        by_provider.setdefault(p, []).append(s)

    for provider, svcs in sorted(by_provider.items()):
        print(f"  {provider} ({len(svcs)})")
        for s in svcs:
            print(f"    {s['slug']:55s} {s['pricing_model']}")

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
