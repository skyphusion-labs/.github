#!/usr/bin/env bash
# Upload generated social preview PNGs to GitHub repos via the REST API.
# Requires: gh auth with repo admin on skyphusion-labs (and skyphusion for profile repo).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
OUT="$ROOT/output/social-preview"

if ! command -v gh >/dev/null; then
  echo "gh CLI required" >&2
  exit 1
fi

shopt -s nullglob
files=("$OUT"/*.png)
if ((${#files[@]} == 0)); then
  echo "No PNGs in $OUT; run generate.py first." >&2
  exit 1
fi

ok=0
fail=0
for png in "${files[@]}"; do
  base="$(basename "$png" .png)"
  owner="${base%%__*}"
  rest="${base#*__}"
  repo="${rest//_/.}"

  if gh api --method PUT "repos/${owner}/${repo}/social-preview" \
    -H "Content-Type: image/png" \
    --input "$png" >/dev/null 2>&1; then
    echo "uploaded: ${owner}/${repo}"
    ok=$((ok + 1))
  else
    echo "FAILED: ${owner}/${repo}" >&2
    fail=$((fail + 1))
  fi
done

echo "done: ${ok} uploaded, ${fail} failed"
