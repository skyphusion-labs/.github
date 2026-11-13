#!/usr/bin/env bash
# approval-at-head.test.sh -- fc#2386
#
# Drives approval-at-head.py against a local fixture API (approval-at-head-fixtures.py
# serve). The checker's real HTTP and pagination code runs; only the server is fake.
# The server answers only the exact path+query it was given and 404s anything else.
#
# Every case asserts the EXIT BAND and the verdict on the structured channel
# (@event approval-at-head {"verdict": ...}), never prose alone. Green cases run in
# the same suite as red ones, so a checker that refuses everything cannot pass, and
# a checker that passes everything cannot either.
#
# The fixture's head first appears at 12:00:00Z (earliest run). Tolerance is 0 and
# the comparison is strictly after, so the three skew cases pin both sides of it.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$HERE/../../.." && pwd)"
for marker in .github/scripts/tests profile; do
  if [ ! -d "$REPO_ROOT/$marker" ]; then
    echo "REFUSED: ROOT=$REPO_ROOT does not look like the skyphusion-labs/.github tree (missing $marker)."
    exit 2
  fi
done
CHECKER="$HERE/../approval-at-head.py"
FX="$HERE/approval-at-head-fixtures.py"
[ -f "$CHECKER" ] || { echo "FAIL: checker not found at $CHECKER" >&2; exit 1; }
[ -f "$FX" ] || { echo "FAIL: fixtures not found at $FX" >&2; exit 1; }

SCRATCH="$(mktemp -d)"
SRV_PID=""
cleanup() { [ -n "$SRV_PID" ] && kill "$SRV_PID" 2>/dev/null || true; rm -rf "$SCRATCH"; }
trap cleanup EXIT

HEAD=9a7690b9fbf603aaa35f988f647ae7ea6eedf2d1
REPO=skyphusion-labs/pilot
PR=7
ASSERTIONS=0
CASES_RUN=0
FAILS=0

ok()   { ASSERTIONS=$((ASSERTIONS + 1)); }
bad()  { echo "FAIL: $*"; FAILS=$((FAILS + 1)); }

start_server() {
  local d="$1"
  rm -f "$d/port"
  python3 "$FX" serve "$d" "$d/port" &
  SRV_PID=$!
  local i=0
  while [ ! -s "$d/port" ]; do
    i=$((i + 1))
    [ "$i" -le 100 ] || { echo "FAIL: fixture server did not start" >&2; exit 2; }
    python3 -c 'import time; time.sleep(0.05)'
  done
  PORT="$(cat "$d/port")"
}

stop_server() { kill "$SRV_PID" 2>/dev/null || true; wait "$SRV_PID" 2>/dev/null || true; SRV_PID=""; }

# case  expected_rc  expected_verdict
run_case() {
  local name="$1" want_rc="$2" want_verdict="$3" sha="${4:-$HEAD}"
  local d="$SCRATCH/$name"
  mkdir -p "$d"
  python3 "$FX" mkcase "$d" "$name"
  start_server "$d"
  set +e
  GITHUB_API_URL="http://127.0.0.1:$PORT" GH_TOKEN="" \
    python3 "$CHECKER" --repo "$REPO" --pr "$PR" --head-sha "$sha" > "$d/out" 2> "$d/err"
  local rc=$?
  set -e
  stop_server
  CASES_RUN=$((CASES_RUN + 1))
  if [ "$rc" -eq "$want_rc" ]; then ok; else bad "$name: rc=$rc want $want_rc"; sed 's/^/    /' "$d/out" "$d/err"; fi
  if grep -q "^@event approval-at-head {.*\"verdict\": \"$want_verdict\"" "$d/out"; then ok
  else bad "$name: no @event verdict $want_verdict"; sed 's/^/    /' "$d/out"; fi
  echo "case $name: rc=$rc verdict=$want_verdict"
}

# ---- green: an approval after the head first appeared ------------------------------
run_case fresh                0 PASS
run_case two-one-fresh        0 PASS
run_case reapproved           0 PASS
run_case skew-after-3s        0 PASS
run_case runs-paginated       0 PASS
run_case reviews-paginated    0 PASS

# ---- red: no approval at this head --------------------------------------------------
run_case stale-update-branch  1 FAIL
run_case none                 1 FAIL
run_case comment-only         1 FAIL
run_case dismissed            1 FAIL
run_case two-both-stale       1 FAIL
run_case approve-then-changes 1 FAIL
run_case skew-before-3s       1 FAIL
run_case skew-equal           1 FAIL
run_case fresh-wrong-commit   1 FAIL
run_case stranger             1 FAIL
run_case head-moved           1 FAIL

# ---- red: could not measure (exit 2 is never a pass) --------------------------------
run_case zero-runs            2 COULD_NOT_MEASURE
run_case reviews-500          2 COULD_NOT_MEASURE
run_case run-wrong-sha        2 COULD_NOT_MEASURE
run_case bad-timestamp        2 COULD_NOT_MEASURE

# ---- --retrigger: the review event re-runs the pull_request run (fc#2386) -----------
# Only the pull_request suite may carry the required context: a red run in one suite
# blocks the merge even when a newer run in another suite is green (measured). So the
# review event re-runs that suite. These cases pin: it waits for a running run, it
# POSTs the re-run exactly once, and every way it cannot do that is exit 2.
run_rt() {
  local name="$1" want_rc="$2" want_post="$3"
  local d="$SCRATCH/$name"
  mkdir -p "$d"
  python3 "$FX" mkcase "$d" "$name"
  start_server "$d"
  set +e
  GITHUB_API_URL="http://127.0.0.1:$PORT" GH_TOKEN="" python3 "$CHECKER" --retrigger \
    --repo "$REPO" --head-sha "$HEAD" --workflow approval-at-head.yml --polls 3 --interval 0 \
    > "$d/out" 2> "$d/err"
  local rc=$?
  set -e
  stop_server
  CASES_RUN=$((CASES_RUN + 1))
  if [ "$rc" -eq "$want_rc" ]; then ok; else bad "$name: rc=$rc want $want_rc"; sed 's/^/    /' "$d/out" "$d/err"; fi
  local posts
  posts="$(grep -c '^POST ' "$d/requests.log" || true)"
  if [ "$posts" -eq "$want_post" ]; then ok; else bad "$name: $posts POST(s), want $want_post"; fi
  echo "case $name: rc=$rc posts=$posts"
}
run_rt rt-completed 0 1
run_rt rt-wait      0 1
run_rt rt-never     2 0
run_rt rt-none      2 0
run_rt rt-wrong-sha 2 0
run_rt rt-refused   2 1
if grep -q '"verdict": "RERUN_REQUESTED"' "$SCRATCH/rt-completed/out"; then ok
else bad "rt-completed: no RERUN_REQUESTED event"; fi
if grep -qx "POST /repos/$REPO/actions/runs/55/rerun" "$SCRATCH/rt-completed/requests.log"; then ok
else bad "rt-completed: the re-run was not POSTed to run 55"; fi
if [ "$(grep -c 'actions/workflows' "$SCRATCH/rt-wait/requests.log")" -eq 2 ]; then ok
else bad "rt-wait: expected 2 polls before the re-run"; fi
if [ "$(grep -c 'actions/workflows' "$SCRATCH/rt-never/requests.log")" -eq 3 ]; then ok
else bad "rt-never: expected exactly the 3-poll budget"; fi

# ---- the short-sha trap: refused before any request is made --------------------------
d="$SCRATCH/short-sha"; mkdir -p "$d"
python3 "$FX" mkcase "$d" fresh
start_server "$d"
set +e
GITHUB_API_URL="http://127.0.0.1:$PORT" python3 "$CHECKER" --repo "$REPO" --pr "$PR" \
  --head-sha "${HEAD:0:7}" > "$d/out" 2>&1
rc=$?
set -e
stop_server
CASES_RUN=$((CASES_RUN + 1))
if [ "$rc" -eq 2 ]; then ok; else bad "short-sha: rc=$rc want 2"; fi
if [ -s "$d/requests.log" ]; then bad "short-sha: a request was made: $(cat "$d/requests.log")"; else ok; fi
echo "case short-sha: rc=$rc"

for argset in "--repo nope --pr 7 --head-sha $HEAD" "--repo $REPO --pr seven --head-sha $HEAD"; do
  set +e
  # shellcheck disable=SC2086
  GITHUB_API_URL="http://127.0.0.1:9" python3 "$CHECKER" $argset > /dev/null 2>&1
  rc=$?
  set -e
  CASES_RUN=$((CASES_RUN + 1))
  if [ "$rc" -eq 2 ]; then ok; else bad "bad input [$argset]: rc=$rc want 2"; fi
done
echo "case bad-input: 2 refusals"

# ---- no server at all: an unreachable API is could-not-measure, not a pass -----------
set +e
GITHUB_API_URL="http://127.0.0.1:9" python3 "$CHECKER" --repo "$REPO" --pr "$PR" --head-sha "$HEAD" > /dev/null 2>&1
rc=$?
set -e
CASES_RUN=$((CASES_RUN + 1))
if [ "$rc" -eq 2 ]; then ok; else bad "unreachable API: rc=$rc want 2"; fi
echo "case unreachable: rc=$rc"

# ---- the instrument asked the full-sha question, and read page 2 ---------------------
if grep -qx "/repos/$REPO/actions/runs?head_sha=$HEAD&per_page=100" "$SCRATCH/fresh/requests.log"; then ok
else bad "fresh: the runs query was not the full-sha form"; cat "$SCRATCH/fresh/requests.log"; fi
if grep -q "page=2" "$SCRATCH/runs-paginated/requests.log"; then ok
else bad "runs-paginated: page 2 was never requested"; fi

# ---- every fixture case is driven above (a case added but not run is not a test) -----
while IFS= read -r c; do
  if [ -d "$SCRATCH/$c" ]; then ok; else bad "fixture case $c is defined but not driven"; fi
done < <(python3 "$FX" cases)

echo "cases_run=$CASES_RUN"
echo "assertions=$ASSERTIONS"
if [ "$FAILS" -ne 0 ]; then
  echo "approval-at-head self-test: $FAILS FAILURE(S)"
  exit 1
fi
echo "approval-at-head self-test: OK"
