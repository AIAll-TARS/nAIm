# Security Audit — Open-source Readiness

Date: 2026-03-19
Owner: PG

## Scope

- Current tracked files (`HEAD`)
- Git history scan for secret-like patterns

## Patterns checked

- `moltbook_sk_...`
- `apiale_vps_token_...`
- hardcoded write API key constants
- bearer token strings in docs/scripts

## Result

### 1) Current tree (`HEAD`)

Status: **PASS**

- Hardcoded keys removed from import scripts.
- `.env.example` sanitized.
- `handoff.md` sanitized to public-safe summary.

### 2) Git history

Status: **FAIL (hard gate)**

- Historical commits contain secret-like tokens and hardcoded keys.
- This means repository is **not safe to make public** until history is rewritten and exposed keys rotated.

## Required actions before public flip

1. Rotate all previously exposed credentials (API keys, tokens).
2. Rewrite git history to remove secret material (BFG or `git filter-repo`).
3. Force-push cleaned history to remote.
4. Re-run history scan and confirm zero matches.

## Suggested history cleanup command (example)

```bash
# Example only — run from a fresh mirror clone
# git filter-repo is preferred over filter-branch

git clone --mirror <repo-url> naim-clean.git
cd naim-clean.git

# Replace secrets using a replacement file
# format: literal:<old>==><new>
# run:
git filter-repo --replace-text ../replacements.txt

git push --force --all
git push --force --tags
```

## Publication gate

Do **not** change GitHub visibility to public until history cleanup + key rotation is complete and verified.
