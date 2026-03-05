"""
Seed the DB with initial categories and a starter set of real API services.
Run once: python -m app.seed
sAIge to validate each service against live APIs before adding more.
"""
from app.database import SessionLocal, engine
from app.models import Base, Category, Service

CATEGORIES = [
    {"slug": "tts", "label": "Text to Speech"},
    {"slug": "stt", "label": "Speech to Text"},
    {"slug": "llm", "label": "Large Language Models"},
    {"slug": "image-gen", "label": "Image Generation"},
    {"slug": "embeddings", "label": "Embeddings"},
    {"slug": "search", "label": "Search"},
    {"slug": "code", "label": "Code Generation"},
    {"slug": "other", "label": "Other"},
]

SERVICES = [
    {
        "slug": "elevenlabs-tts",
        "name": "ElevenLabs TTS",
        "canonical_provider": "ElevenLabs",
        "category_slug": "tts",
        "description": "High-quality AI voice synthesis with voice cloning support.",
        "docs_url": "https://elevenlabs.io/docs/api-reference",
        "base_url": "https://api.elevenlabs.io",
        "auth_type": "api_key",
        "pricing_model": "usage_based",
        "pricing_notes": "Free tier: 10k chars/mo. Paid from $5/mo.",
        "status": "approved",
    },
    {
        "slug": "openai-tts",
        "name": "OpenAI TTS",
        "canonical_provider": "OpenAI",
        "category_slug": "tts",
        "description": "OpenAI text-to-speech API with multiple voice options.",
        "docs_url": "https://platform.openai.com/docs/guides/text-to-speech",
        "base_url": "https://api.openai.com/v1/audio/speech",
        "auth_type": "api_key",
        "pricing_model": "per_request",
        "pricing_notes": "$15/1M chars for tts-1, $30/1M chars for tts-1-hd.",
        "status": "approved",
    },
    {
        "slug": "openai-whisper",
        "name": "OpenAI Whisper STT",
        "canonical_provider": "OpenAI",
        "category_slug": "stt",
        "description": "Speech-to-text transcription via OpenAI Whisper model.",
        "docs_url": "https://platform.openai.com/docs/guides/speech-to-text",
        "base_url": "https://api.openai.com/v1/audio/transcriptions",
        "auth_type": "api_key",
        "pricing_model": "per_request",
        "pricing_notes": "$0.006/minute.",
        "status": "approved",
    },
    {
        "slug": "anthropic-claude",
        "name": "Anthropic Claude API",
        "canonical_provider": "Anthropic",
        "category_slug": "llm",
        "description": "Claude family of LLMs — Haiku, Sonnet, Opus. Strong reasoning and tool use.",
        "docs_url": "https://docs.anthropic.com",
        "base_url": "https://api.anthropic.com",
        "auth_type": "api_key",
        "pricing_model": "per_request",
        "pricing_notes": "From $0.25/M tokens (Haiku) to $15/M tokens (Opus).",
        "status": "approved",
    },
    {
        "slug": "openai-gpt4",
        "name": "OpenAI GPT-4o",
        "canonical_provider": "OpenAI",
        "category_slug": "llm",
        "description": "OpenAI flagship multimodal LLM with vision and tool use.",
        "docs_url": "https://platform.openai.com/docs",
        "base_url": "https://api.openai.com/v1",
        "auth_type": "api_key",
        "pricing_model": "per_request",
        "pricing_notes": "$2.50/M input tokens, $10/M output tokens.",
        "status": "approved",
    },
    {
        "slug": "deepseek-chat",
        "name": "DeepSeek Chat API",
        "canonical_provider": "DeepSeek",
        "category_slug": "llm",
        "description": "Cost-efficient LLM with strong coding and reasoning performance.",
        "docs_url": "https://platform.deepseek.com/api-docs",
        "base_url": "https://api.deepseek.com",
        "auth_type": "api_key",
        "pricing_model": "per_request",
        "pricing_notes": "From $0.07/M tokens — very low cost.",
        "status": "approved",
    },
    {
        "slug": "openai-embeddings",
        "name": "OpenAI Embeddings",
        "canonical_provider": "OpenAI",
        "category_slug": "embeddings",
        "description": "Text embedding models for semantic search and retrieval.",
        "docs_url": "https://platform.openai.com/docs/guides/embeddings",
        "base_url": "https://api.openai.com/v1/embeddings",
        "auth_type": "api_key",
        "pricing_model": "per_request",
        "pricing_notes": "$0.02/M tokens (text-embedding-3-small).",
        "status": "approved",
    },
    {
        "slug": "stability-image-gen",
        "name": "Stability AI Image Generation",
        "canonical_provider": "Stability AI",
        "category_slug": "image-gen",
        "description": "Stable Diffusion image generation via API.",
        "docs_url": "https://platform.stability.ai/docs/api-reference",
        "base_url": "https://api.stability.ai",
        "auth_type": "api_key",
        "pricing_model": "per_request",
        "pricing_notes": "From $0.01 per image.",
        "status": "approved",
    },
    {
        "slug": "serper-search",
        "name": "Serper Google Search API",
        "canonical_provider": "Serper",
        "category_slug": "search",
        "description": "Real-time Google search results via REST API. Popular with AI agents.",
        "docs_url": "https://serper.dev/docs",
        "base_url": "https://google.serper.dev",
        "auth_type": "api_key",
        "pricing_model": "per_request",
        "pricing_notes": "Free tier: 2500 queries. Paid from $50/50k queries.",
        "status": "approved",
    },
    {
        "slug": "github-copilot-api",
        "name": "GitHub Copilot API",
        "canonical_provider": "GitHub",
        "category_slug": "code",
        "description": "AI code completion and generation via GitHub Copilot.",
        "docs_url": "https://docs.github.com/en/copilot",
        "base_url": "https://api.githubcopilot.com",
        "auth_type": "oauth",
        "pricing_model": "subscription",
        "pricing_notes": "$10/mo individual, $19/mo business.",
        "status": "approved",
    },
]


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        for cat in CATEGORIES:
            if not db.query(Category).filter(Category.slug == cat["slug"]).first():
                db.add(Category(**cat))

        db.commit()

        for svc in SERVICES:
            if not db.query(Service).filter(Service.slug == svc["slug"]).first():
                db.add(Service(**svc))

        db.commit()
        print(f"Seeded {len(CATEGORIES)} categories and {len(SERVICES)} services.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
