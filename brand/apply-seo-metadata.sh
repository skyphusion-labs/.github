#!/usr/bin/env bash
# Apply GitHub repository description + homepage from brand/seo-metadata.json.
#
# Requires: gh (authenticated), jq
#
# Usage:
#   ./apply-seo-metadata.sh              # apply catalog to all listed repos
#   ./apply-seo-metadata.sh --dry-run    # print planned updates only
#   ./apply-seo-metadata.sh --check      # exit 1 if live metadata differs
#   ./apply-seo-metadata.sh --repo vivijure
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CATALOG="${SCRIPT_DIR}/seo-metadata.json"

DRY_RUN=false
CHECK=false
FILTER_REPO=""

usage() {
  sed -n '2,11p' "$0" | sed 's/^# \?//'
  exit "${1:-0}"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=true; shift ;;
    --check) CHECK=true; shift ;;
    --repo) FILTER_REPO="$2"; shift 2 ;;
    -h|--help) usage 0 ;;
    *) echo "Unknown option: $1" >&2; usage 1 ;;
  esac
done

for cmd in gh jq; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Missing required command: $cmd" >&2
    exit 1
  fi
done

entries="$(jq -c --arg repo "$FILTER_REPO" '
  [.[] | if ($repo != "" and .repo != $repo) then empty else . end]
' "$CATALOG")"

entry_count="$(jq 'length' <<<"$entries")"
if [[ "$entry_count" -eq 0 ]]; then
  echo "No catalog entries matched filters." >&2
  exit 1
fi

mismatch=0
updated=0

while IFS= read -r entry; do
  owner="$(jq -r '.owner' <<<"$entry")"
  repo="$(jq -r '.repo' <<<"$entry")"
  want_desc="$(jq -r '.description' <<<"$entry")"
  want_home="$(jq -r '.homepage // ""' <<<"$entry")"
  slug="${owner}/${repo}"

  live="$(gh api "repos/${slug}" -q '{description: (.description // ""), homepage: (.homepage // "")}')"
  have_desc="$(jq -r '.description' <<<"$live")"
  have_home="$(jq -r '.homepage' <<<"$live")"

  if [[ "$CHECK" == true ]]; then
    if [[ "$want_desc" != "$have_desc" || "$want_home" != "$have_home" ]]; then
      echo "DRIFT ${slug}"
      echo "  want desc: ${want_desc}"
      echo "  have desc: ${have_desc}"
      echo "  want home: ${want_home}"
      echo "  have home: ${have_home}"
      mismatch=$((mismatch + 1))
    fi
    continue
  fi

  if [[ "$DRY_RUN" == true ]]; then
    if [[ "$want_desc" == "$have_desc" && "$want_home" == "$have_home" ]]; then
      echo "OK   ${slug} unchanged"
    else
      echo "PLAN ${slug}"
      echo "  description: ${want_desc}"
      echo "  homepage:    ${want_home}"
      updated=$((updated + 1))
    fi
    continue
  fi

  echo -n "==> ${slug}... "
  patch_args=(-f "description=${want_desc}")
  if [[ -n "$want_home" ]]; then
    patch_args+=(-f "homepage=${want_home}")
  else
    patch_args+=(-f homepage=)
  fi
  if ! gh api --method PATCH "repos/${slug}" "${patch_args[@]}" >/dev/null 2>&1; then
    if [[ "$(gh api "repos/${slug}" -q .archived 2>/dev/null || echo false)" == "true" ]]; then
      echo "skipped (archived)"
      continue
    fi
    echo "FAILED" >&2
    exit 1
  fi
  echo "done"
  updated=$((updated + 1))
done < <(jq -c '.[]' <<<"$entries")

if [[ "$CHECK" == true ]]; then
  if [[ "$mismatch" -gt 0 ]]; then
    echo "${mismatch} repo(s) differ from brand/seo-metadata.json" >&2
    exit 1
  fi
  echo "All ${entry_count} catalog repo(s) match live metadata."
  exit 0
fi

if [[ "$DRY_RUN" == true ]]; then
  echo "Dry run: ${updated} repo(s) would update."
else
  echo "Applied metadata to ${updated} repo(s)."
fi
