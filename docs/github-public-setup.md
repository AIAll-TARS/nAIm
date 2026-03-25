# GitHub Public Setup Checklist

Use this right before changing repository visibility to public.

## Repository metadata

- Description: `Machine-first API registry for AI agents`
- Website: `https://naim.janis7ewski.org`
- Topics:
  - `ai`
  - `api-registry`
  - `agents`
  - `fastapi`
  - `nextjs`
  - `openapi`
  - `agpl`

## Community features

- Enable Discussions
- Enable Issues
- Add issue templates (optional, recommended)
- Add pull request template (optional, recommended)

## Branch protection

- Protect `main` (or release branch)
- Require PR review
- Require status checks (`Secret scan`, lint/build)

## Visibility gate (must pass)

- [ ] `SECURITY_AUDIT.md` current tree: PASS
- [ ] `SECURITY_AUDIT.md` history: PASS
- [ ] Key rotation confirmed
- [ ] License/docs pack complete
- [ ] Maintainer approved visibility change

Then: Settings → General → Change repository visibility → Public.
