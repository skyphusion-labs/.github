#!/usr/bin/env bash
# Apply GitHub repository topics from brand/topics.json.
#
# Requires: gh (authenticated), jq
# GitHub allows at most 20 topics per repository.
#
# Usage:
#   ./update-topics.sh              # apply catalog to all listed repos
#   ./update-topics.sh --dry-run    # print planned updates, no API writes
#   ./update-topics.sh --check      # exit 1 if live topics differ from catalog
#   ./update-topics.sh --repo vivijure
#   ./update-topics.sh --family vivijure
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CATALOG="${SCRIPT_DIR}/topics.json"
MAX_TOPICS=20

DRY_RUN=false
CHECK=false
FILTER_REPO=""
FILTER_FAMILY=""

usage() {
  sed -n '2,12p' "$0" | sed 's/^# \?//'
  exit "${1:-0}"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=true; shift ;;
    --check) CHECK=true; shift ;;
    --repo) FILTER_REPO="$2"; shift 2 ;;
    --family) FILTER_FAMILY="$2"; shift 2 ;;
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

if [[ ! -f "$CATALOG" ]]; then
  echo "Catalog not found: $CATALOG" >&2
  exit 1
fi

# Validate catalog shape before any API calls.
invalid_count="$(jq -r --argjson max "$MAX_TOPICS" '
  [.[] | select((.topics | length) > $max or (.topics | length) == 0)]
  | length
' "$CATALOG")"
if [[ "$invalid_count" != "0" ]]; then
  echo "Catalog validation failed: every entry needs 1..${MAX_TOPICS} topics." >&2
  jq -r --argjson max "$MAX_TOPICS" '
    .[] | select((.topics | length) > $max or (.topics | length) == 0)
    | "\(.owner)/\(.repo): \(.topics | length) topics"
  ' "$CATALOG" >&2
  exit 1
fi

entries="$(jq -c --arg repo "$FILTER_REPO" --arg family "$FILTER_FAMILY" '
  [.[] |
    if ($repo != "" and .repo != $repo) then empty
    elif ($family != "" and .family != $family) then empty
    else .
    end]
' "$CATALOG")"

entry_count="$(jq 'length' <<<"$entries")"
if [[ "$entry_count" -eq 0 ]]; then
  echo "No catalog entries matched filters." >&2
  exit 1
fi

normalize_topics() {
  jq -c 'sort | unique'
}

fetch_live_topics() {
  local owner="$1" repo="$2"
  gh api "repos/${owner}/${repo}/topics" \
    -H "Accept: application/vnd.github+json" \
    -q '.names | sort'
}

put_topics() {
  local owner="$1" repo="$2" topics_json="$3"
  local body
  body="$(jq -n --argjson names "$topics_json" '{names: $names}')"
  gh api --method PUT "repos/${owner}/${repo}/topics" \
    -H "Accept: application/vnd.github+json" \
    --input - <<<"$body" >/dev/null
}

mismatch=0
updated=0
unchanged=0

while IFS= read -r entry; do
  owner="$(jq -r '.owner' <<<"$entry")"
  repo="$(jq -r '.repo' <<<"$entry")"
  family="$(jq -r '.family' <<<"$entry")"
  want="$(jq -c '.topics | sort | unique' <<<"$entry")"
  slug="${owner}/${repo}"

  if [[ "$CHECK" == true ]]; then
    have="$(fetch_live_topics "$owner" "$repo" | normalize_topics)"
    if [[ "$want" != "$have" ]]; then
      echo "DRIFT ${slug} (family=${family})"
      echo "  want: $(jq -r 'join(", ")' <<<"$want")"
      echo "  have: $(jq -r 'join(", ")' <<<"$have")"
      mismatch=$((mismatch + 1))
    fi
    continue
  fi

  if [[ "$DRY_RUN" == true ]]; then
    have="$(fetch_live_topics "$owner" "$repo" | normalize_topics)"
    if [[ "$want" == "$have" ]]; then
      echo "OK   ${slug} (${family}) unchanged"
      unchanged=$((unchanged + 1))
    else
      echo "PLAN ${slug} (${family}) -> $(jq -r 'join(", ")' <<<"$want")"
      updated=$((updated + 1))
    fi
    continue
  fi

  echo -n "==> ${slug} (${family}, $(jq 'length' <<<"$want") topics)... "
  put_topics "$owner" "$repo" "$want"
  echo "done"
  updated=$((updated + 1))
done < <(jq -c '.[]' <<<"$entries")

if [[ "$CHECK" == true ]]; then
  if [[ "$mismatch" -gt 0 ]]; then
    echo "${mismatch} repo(s) differ from brand/topics.json" >&2
    exit 1
  fi
  echo "All ${entry_count} catalog repo(s) match live topics."
  exit 0
fi

if [[ "$DRY_RUN" == true ]]; then
  echo "Dry run: ${updated} would update, ${unchanged} already match."
else
  echo "Applied topics to ${updated} repo(s)."
fi
