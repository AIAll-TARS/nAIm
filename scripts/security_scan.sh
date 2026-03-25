#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "== HEAD scan =="
git grep -nE 'moltbook_sk_|apiale_vps_token_|NAIM_KEY\s*=\s*"|MOLTBOOK_API_KEY=.*moltbook|Authorization: Bearer [A-Za-z0-9_-]{20,}' -- . || true

echo
echo "== History sample scan (latest 200 commits) =="
git rev-list --all | head -n 200 | while read -r c; do
  git grep -nE 'moltbook_sk_|apiale_vps_token_|7f59b1cd249b47d6a22624098a8654d0c5ed6a3d' "$c" -- . 2>/dev/null | sed "s#^#$c:#"
done | head -n 200 || true

echo
echo "Done."
