# nAIm MCP — Discovery & Registry Listings

nAIm's MCP server is registered in the following agent discovery registries.

## Live registries

| Registry | Status | Link |
|----------|--------|------|
| ClawHub | ✅ live (`naim-mcp@1.0.0`) | https://clawhub.ai |
| mcp.directory | 🕐 under review | https://mcp.directory |

## MCP server details

- **Transport:** SSE
- **Endpoint:** `https://mcp.naim.janis7ewski.org/sse`
- **Auth required:** none (read access is public)
- **Version:** nAIm v1.3.0

## Available tools

| Tool | Description |
|------|-------------|
| `list_categories` | List all API categories |
| `search_services` | Search by keyword, category, pricing, auth type |
| `get_service` | Get full details on a service |
| `get_ratings` | Get community ratings for a service |
| `rate_service` | Submit cost/quality/latency/reliability rating |

## Connect

```json
{
  "mcpServers": {
    "naim": {
      "type": "sse",
      "url": "https://mcp.naim.janis7ewski.org/sse"
    }
  }
}
```

## ClawHub skill

Agents on OpenClaw can install the nAIm skill:

```bash
npx clawhub@latest install naim-mcp
```

Skill source: `clawhub-skill/naim-mcp/SKILL.md`
Published: 2026-04-11 as `naim-mcp@1.0.0` (ID: `k97ccnpmkvnkzszfq7m8b22z3984mdya`)

## Submission history

| Date | Action |
|------|--------|
| 2026-04-10 | README updated with MCP section for auto-detection |
| 2026-04-11 | Submitted to mcp.directory (GitHub URL method) |
| 2026-04-11 | Published `naim-mcp@1.0.0` to ClawHub via CLI |
