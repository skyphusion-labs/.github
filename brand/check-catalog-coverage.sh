#!/usr/bin/env bash
# Fail when a public non-archived skyphusion-labs repo is missing from the
# discoverability catalogs (topics.json / seo-metadata.json).
#
# The existing --check scripts only iterate catalog rows, so a brand-new
# public repo that never got a catalog entry would otherwise pass green.
# See skyphusion-labs/.github#17.
#
# Requires: gh (authenticated), jq
#
# Usage:
#   ./check-catalog-coverage.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOPICS="${SCRIPT_DIR}/topics.json"
SEO="${SCRIPT_DIR}/seo-metadata.json"
OWNER="${CATALOG_OWNER:-skyphusion-labs}"

for cmd in gh jq; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Missing required command: $cmd" >&2
    exit 1
  fi
done

for f in "$TOPICS" "$SEO"; do
  if [[ ! -f "$f" ]]; then
    echo "Catalog not found: $f" >&2
    exit 1
  fi
done

# Public, non-archived repos under the org (name only).
mapfile -t public_repos < <(
  gh repo list "$OWNER" --visibility public --limit 200 --json name,isArchived \
    --jq '.[] | select(.isArchived | not) | .name' | sort -u
)

if [[ "${#public_repos[@]}" -eq 0 ]]; then
  echo "No public repos returned for ${OWNER}; refusing to pass vacuously." >&2
  exit 1
fi

topics_repos="$(jq -r --arg o "$OWNER" '[.[] | select(.owner == $o) | .repo] | unique | .[]' "$TOPICS" | sort -u)"
seo_repos="$(jq -r --arg o "$OWNER" '[.[] | select(.owner == $o) | .repo] | unique | .[]' "$SEO" | sort -u)"

missing_topics=()
missing_seo=()
for repo in "${public_repos[@]}"; do
  if ! grep -Fxq "$repo" <<<"$topics_repos"; then
    missing_topics+=("$repo")
  fi
  if ! grep -Fxq "$repo" <<<"$seo_repos"; then
    missing_seo+=("$repo")
  fi
done

fail=0
if [[ "${#missing_topics[@]}" -gt 0 ]]; then
  fail=1
  echo "Public repos missing from brand/topics.json:" >&2
  printf '  %s\n' "${missing_topics[@]}" >&2
fi
if [[ "${#missing_seo[@]}" -gt 0 ]]; then
  fail=1
  echo "Public repos missing from brand/seo-metadata.json:" >&2
  printf '  %s\n' "${missing_seo[@]}" >&2
fi

if [[ "$fail" -ne 0 ]]; then
  echo "Reverse-coverage check failed. Add catalog rows for each missing public repo (see brand/README.md)." >&2
  exit 1
fi

echo "All ${#public_repos[@]} public non-archived ${OWNER} repo(s) are present in topics.json and seo-metadata.json."
