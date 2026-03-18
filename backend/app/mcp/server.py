"""
nAIm MCP Server

Exposes nAIm registry tools to any MCP-compatible AI agent.

Tools:
  - list_categories       — list all service categories
  - search_services       — search by category and/or keyword
  - get_service           — full detail for one service
  - get_ratings           — aggregated ratings for a service
  - submit_rating         — rate a service

Transports:
  - stdio  (Claude Desktop, Claude Code, local agents)
  - SSE    (remote HTTP agents) — run with --sse flag

Usage:
  stdio:  python -m app.mcp.server
  SSE:    python -m app.mcp.server --sse --port 8001
"""

import asyncio
import json
import os
import sys
import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

API_BASE = os.getenv("NAIM_API_URL", "http://localhost:18792")

app = Server("nAIm")


async def _get(path: str, params: dict = None) -> dict | list:
    async with httpx.AsyncClient(base_url=API_BASE, timeout=10) as client:
        r = await client.get(path, params=params or {})
        r.raise_for_status()
        return r.json()


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="list_categories",
            description="List all available API service categories in the nAIm registry (e.g. tts, llm, embeddings).",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="search_services",
            description=(
                "Search the nAIm registry for API services. "
                "Filter by category slug (e.g. 'tts', 'llm') and/or a keyword to match against name, provider, or description."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Category slug to filter by (e.g. 'tts', 'stt', 'llm', 'embeddings'). Optional.",
                    },
                    "query": {
                        "type": "string",
                        "description": "Keyword to match against service name, provider, or description. Optional.",
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="get_service",
            description="Get full details for a specific API service by its ID, including docs URL, pricing, and auth type.",
            inputSchema={
                "type": "object",
                "properties": {
                    "service_id": {
                        "type": "string",
                        "description": "The service UUID from search_services results.",
                    }
                },
                "required": ["service_id"],
            },
        ),
        Tool(
            name="get_ratings",
            description="Get aggregated agent ratings for a service — overall, quality, latency, reliability, cost scores.",
            inputSchema={
                "type": "object",
                "properties": {
                    "service_id": {
                        "type": "string",
                        "description": "The service UUID.",
                    }
                },
                "required": ["service_id"],
            },
        ),
        Tool(
            name="submit_rating",
            description=(
                "Submit a rating for an API service you have used. "
                "All scores are 1.0 (worst) to 5.0 (best)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "service_id": {"type": "string", "description": "The service UUID."},
                    "cost_score": {"type": "number", "description": "Cost value (1-5). 5 = very cheap."},
                    "quality_score": {"type": "number", "description": "Output quality (1-5)."},
                    "latency_score": {"type": "number", "description": "Response speed (1-5). 5 = very fast."},
                    "reliability_score": {"type": "number", "description": "Uptime/reliability (1-5)."},
                    "agent_id": {"type": "string", "description": "Your agent identifier. Optional."},
                    "notes": {"type": "string", "description": "Free-text notes. Optional."},
                },
                "required": ["service_id", "cost_score", "quality_score", "latency_score", "reliability_score"],
            },
        ),
        Tool(
            name="rate_service",
            description=(
                "Rate an API service by its slug (e.g. 'groq-llm', 'elevenlabs-tts'). "
                "Easier to use than submit_rating — no UUID needed. "
                "Use search_services first to find the slug if unsure. "
                "All scores are 1 (worst) to 5 (best)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "service_slug": {
                        "type": "string",
                        "description": "The service slug, e.g. 'groq-llm', 'elevenlabs-tts', 'deepgram-stt'.",
                    },
                    "cost_score": {"type": "number", "description": "Cost value 1-5. 5 = very cheap / great value."},
                    "quality_score": {"type": "number", "description": "Output quality 1-5. 5 = excellent."},
                    "latency_score": {"type": "number", "description": "Response speed 1-5. 5 = very fast."},
                    "reliability_score": {"type": "number", "description": "Uptime and stability 1-5. 5 = rock solid."},
                    "agent_handle": {
                        "type": "string",
                        "description": "Your agent handle or identifier, e.g. '@myagent'. Optional but encouraged.",
                    },
                    "notes": {
                        "type": "string",
                        "description": "Free-text notes — specific failure modes, use case context, observations. Optional.",
                    },
                },
                "required": ["service_slug", "cost_score", "quality_score", "latency_score", "reliability_score"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    try:
        if name == "list_categories":
            data = await _get("/v1/categories")
            result = "\n".join(f"- {c['slug']}: {c['label']}" for c in data)
            return [TextContent(type="text", text=f"Available categories:\n{result}")]

        elif name == "search_services":
            params = {}
            if arguments.get("category"):
                params["category"] = arguments["category"]
            data = await _get("/v1/services", params)

            query = arguments.get("query", "").lower()
            if query:
                data = [
                    s for s in data
                    if query in s["name"].lower()
                    or query in s["canonical_provider"].lower()
                    or query in s["description"].lower()
                ]

            if not data:
                return [TextContent(type="text", text="No services found matching your criteria.")]

            lines = []
            for s in data:
                rating_str = f"{s['avg_rating']:.1f}/5 ({s['rating_count']} ratings)" if s.get("avg_rating") else "no ratings yet"
                lines.append(
                    f"Slug: {s['slug']}\n"
                    f"  Name: {s['name']} ({s['canonical_provider']})\n"
                    f"  Category: {s['category_slug']}\n"
                    f"  Rating: {rating_str}\n"
                    f"  Pricing: {s['pricing_model']} — {s.get('pricing_notes', 'N/A')}\n"
                    f"  Auth: {s['auth_type']}\n"
                    f"  Description: {s['description']}"
                )
            return [TextContent(type="text", text="\n\n".join(lines))]

        elif name == "get_service":
            s = await _get(f"/v1/services/{arguments['service_id']}")
            text = (
                f"Name: {s['name']}\n"
                f"Provider: {s['canonical_provider']}\n"
                f"Category: {s['category_slug']}\n"
                f"Description: {s['description']}\n"
                f"Base URL: {s['base_url']}\n"
                f"Docs: {s['docs_url']}\n"
                f"Auth: {s['auth_type']}\n"
                f"Pricing: {s['pricing_model']} — {s.get('pricing_notes', 'N/A')}\n"
                f"Verified: {s['verified']}"
            )
            return [TextContent(type="text", text=text)]

        elif name == "get_ratings":
            r = await _get(f"/v1/services/{arguments['service_id']}/ratings")
            if r["count"] == 0:
                return [TextContent(type="text", text="No ratings yet for this service.")]
            text = (
                f"Ratings ({r['count']} total):\n"
                f"  Overall:     {r['avg_overall']}/5\n"
                f"  Quality:     {r['avg_quality']}/5\n"
                f"  Latency:     {r['avg_latency']}/5\n"
                f"  Reliability: {r['avg_reliability']}/5\n"
                f"  Cost:        {r['avg_cost']}/5"
            )
            return [TextContent(type="text", text=text)]

        elif name == "rate_service":
            # Look up service by slug
            all_services = await _get("/v1/services")
            slug = arguments["service_slug"].lower().strip()
            match = next((s for s in all_services if s["slug"] == slug), None)
            if not match:
                close = [s["slug"] for s in all_services if slug in s["slug"] or s["slug"] in slug]
                hint = f" Did you mean: {', '.join(close[:3])}?" if close else ""
                return [TextContent(type="text", text=f"Service '{slug}' not found.{hint}")]

            payload = {
                "cost_score": arguments["cost_score"],
                "quality_score": arguments["quality_score"],
                "latency_score": arguments["latency_score"],
                "reliability_score": arguments["reliability_score"],
                "agent_id": arguments.get("agent_handle"),
                "notes": arguments.get("notes"),
            }
            async with httpx.AsyncClient(base_url=API_BASE, timeout=10) as client:
                r = await client.post(f"/v1/services/{match['id']}/ratings", json=payload)
                if r.status_code == 409:
                    return [TextContent(type="text", text=f"You have already rated '{slug}'.")]
                r.raise_for_status()

            avg = match.get("avg_rating")
            avg_str = f" (registry avg: {avg:.1f}/5)" if avg else ""
            return [TextContent(
                type="text",
                text=(
                    f"Rating submitted for {match['name']}{avg_str}.\n"
                    f"  Cost: {arguments['cost_score']}/5\n"
                    f"  Quality: {arguments['quality_score']}/5\n"
                    f"  Latency: {arguments['latency_score']}/5\n"
                    f"  Reliability: {arguments['reliability_score']}/5"
                    + (f"\n  Notes: {arguments['notes']}" if arguments.get("notes") else "")
                ),
            )]

        elif name == "submit_rating":
            async with httpx.AsyncClient(base_url=API_BASE, timeout=10) as client:
                payload = {
                    "cost_score": arguments["cost_score"],
                    "quality_score": arguments["quality_score"],
                    "latency_score": arguments["latency_score"],
                    "reliability_score": arguments["reliability_score"],
                    "agent_id": arguments.get("agent_id"),
                    "notes": arguments.get("notes"),
                }
                r = await client.post(f"/v1/services/{arguments['service_id']}/ratings", json=payload)
                if r.status_code == 409:
                    return [TextContent(type="text", text="You have already rated this service.")]
                r.raise_for_status()
            return [TextContent(type="text", text="Rating submitted successfully.")]

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except httpx.HTTPStatusError as e:
        return [TextContent(type="text", text=f"API error: {e.response.status_code} — {e.response.text}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main_stdio():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


def main():
    if "--sse" in sys.argv:
        # SSE transport for remote agents
        from mcp.server.sse import SseServerTransport
        from starlette.applications import Starlette
        from starlette.routing import Route, Mount
        import uvicorn

        port = int(sys.argv[sys.argv.index("--port") + 1]) if "--port" in sys.argv else 8001
        sse = SseServerTransport("/messages")

        async def handle_sse(request):
            async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
                await app.run(streams[0], streams[1], app.create_initialization_options())

        starlette_app = Starlette(routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages", app=sse.handle_post_message),
        ])
        uvicorn.run(starlette_app, host="0.0.0.0", port=port)
    else:
        asyncio.run(main_stdio())


if __name__ == "__main__":
    main()
