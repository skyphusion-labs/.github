#!/usr/bin/env python3
"""approval-at-head.py -- fc#2386

Pass only when an approval was given AFTER the remote first saw the PR head.

THE RULING (Conrad, 2026-11-10, on fc#2386): an automatic check blocks a merge
when the only approval predates the merged sha. #2614 turned on
require_last_push_approval, and it does not catch this. `gh pr update-branch`
is not a "reviewable push", so neither require_last_push_approval nor
dismiss_stale_reviews_on_push reacts to it, and the old approval's commit_id
is re-pointed at the new head (fc#1657). This check is the mechanism.

THE PREDICATE. A reviewer counts when ALL of these hold:
  * the reviewer's LATEST decisive review (APPROVED, CHANGES_REQUESTED or
    DISMISSED; COMMENTED does not change a decision) is APPROVED
  * that review's commit_id is the current head sha
  * that review's submitted_at is STRICTLY AFTER head_first_seen
  * the reviewer is not the PR author, and author_association is OWNER,
    MEMBER or COLLABORATOR (a stranger's approval on a public repo does not
    count toward the ruleset either)
The check passes when at least one reviewer counts.

commit_id alone cannot do this: update-branch rewrites it forward. submitted_at
alone cannot do it either: a reviewer on a stale page can approve an older
head after the push. Together they can.

THE ARRIVAL INSTRUMENT: head_first_seen is the EARLIEST created_at across
GET /repos/{o}/{r}/actions/runs?head_sha=<FULL 40-char sha>, all pages.
Why this and not the PR timeline: timeline `committed` events carry the
commit's own date, which is set on the author's machine and predates the push;
`head_ref_force_pushed` covers force pushes only. A workflow run is created by
GitHub on GitHub's clock when the push event is processed, so it is the only
server-side arrival time available for an ordinary push and for update-branch.
The caller of this check runs on pull_request synchronize, so every head sha
the gate judges has at least one run of its own.

Its error direction is RED, never GREEN: run creation can lag the push (queue
delay), which makes head_first_seen LATER than the true arrival, which can only
make a genuinely fresh approval look stale. A lag cannot make a stale approval
look fresh. The cost of the lag is an extra re-approval, never a false pass.

TOLERANCE: 0 seconds, comparison strictly greater. Both timestamps come from
GitHub's own clock, at one-second resolution. Any positive tolerance admits an
approval given up to that many seconds BEFORE the push, which is exactly the
defect this check exists to catch. Equal seconds is RED: in that second the
order cannot be known, and the remedy for a false red is one re-approval.

FULL SHA ONLY. actions/runs?head_sha= does exact matching. An abbreviation
returns HTTP 200 with total_count 0 (measured on fc#2386), so a short sha is
refused before any call, and zero runs for a full sha is COULD NOT MEASURE.

EXIT BANDS. 0 PASS. 1 FINDING (no approval at the head). 2 COULD NOT MEASURE
(bad input, API error, unreadable payload, zero runs). 2 is never a pass, and
both 1 and 2 turn the required check red.

One structured line is printed for machines:
  @event approval-at-head {json}

WHY THE REVIEW EVENT RE-RUNS INSTEAD OF JUDGING (measured 2026-11-12, fc#2386).
Every workflow run is its own check suite. A ruleset requiring a context is
FAILING when ANY suite's latest run of that name failed, even if a NEWER run
in another suite passed. Measured on skyphusion-strummer/check-resolution-test
PR 1: a red pull_request run and a later green pull_request_review run on one
sha, `gh pr checks` shows both, mergeStateStatus BLOCKED, and PUT /merge
returned 405 "Required status check is failing". So only the pull_request
suite may produce the required context. The review event runs --retrigger,
which waits for that run to finish and re-runs it. A re-run is a new attempt
in the SAME suite, it replaces that suite's check run, and it judges LIVE
state. Measured on PR 2: after the re-run, filter=latest shows one green
row, mergeStateStatus CLEAN, the merge succeeded, rule-suite result pass.

Usage:
  approval-at-head.py --repo OWNER/REPO --pr N --head-sha SHA40
  approval-at-head.py --retrigger --repo OWNER/REPO --head-sha SHA40 \
      --workflow approval-at-head.yml
  --retrigger exits 0 when the re-run was requested, 2 when it could not be
  (no run for the sha, the run never finished, the API refused).
Environment: GH_TOKEN (read: pull-requests, actions), GITHUB_API_URL
(defaults to https://api.github.com).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

SHA40 = re.compile(r"^[0-9a-f]{40}$")
REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
DECISIVE = {"APPROVED", "CHANGES_REQUESTED", "DISMISSED"}
TRUSTED = {"OWNER", "MEMBER", "COLLABORATOR"}
NEXT_LINK = re.compile(r'<([^>]+)>;\s*rel="next"')
MAX_PAGES = 50


class CouldNotMeasure(Exception):
    pass


def emit(verdict, **fields):
    rec = {"verdict": verdict}
    rec.update(fields)
    print("@event approval-at-head " + json.dumps(rec, sort_keys=True))


def parse_ts(value, what):
    if not isinstance(value, str):
        raise CouldNotMeasure(f"{what} is missing or not a string: {value!r}")
    try:
        ts = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError as exc:
        raise CouldNotMeasure(f"{what} is not an RFC3339 UTC timestamp: {value!r}") from exc
    return ts.replace(tzinfo=timezone.utc)


def get(url, token, method="GET"):
    req = urllib.request.Request(url, method=method, data=b"" if method == "POST" else None)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read()
            link = resp.headers.get("Link", "") or ""
    except urllib.error.HTTPError as exc:
        raise CouldNotMeasure(f"HTTP {exc.code} from {url}") from exc
    except (urllib.error.URLError, OSError) as exc:
        raise CouldNotMeasure(f"no response from {url}: {exc}") from exc
    if method == "POST" and not body.strip():
        return {}, None
    try:
        data = json.loads(body)
    except ValueError as exc:
        raise CouldNotMeasure(f"payload from {url} is not JSON") from exc
    m = NEXT_LINK.search(link)
    return data, (m.group(1) if m else None)


def get_all(url, token, key=None):
    """Every page. key=None means each page is a JSON array; otherwise the
    array is page[key]. A missing key or a non-array is COULD NOT MEASURE."""
    items, pages = [], 0
    while url:
        pages += 1
        if pages > MAX_PAGES:
            raise CouldNotMeasure(f"more than {MAX_PAGES} pages; refusing to judge a truncated list")
        data, url = get(url, token)
        page = data if key is None else (data.get(key) if isinstance(data, dict) else None)
        if not isinstance(page, list):
            raise CouldNotMeasure(f"page {pages} carries no list" + (f" under {key!r}" if key else ""))
        items.extend(page)
    return items


def head_first_seen(api, repo, sha, token):
    runs = get_all(f"{api}/repos/{repo}/actions/runs?head_sha={sha}&per_page=100", token, "workflow_runs")
    if not runs:
        raise CouldNotMeasure(
            f"actions/runs?head_sha={sha} returned 0 runs. The caller runs on every push, "
            "so zero means the instrument produced nothing, not that the sha never arrived")
    stamps = []
    for r in runs:
        if not isinstance(r, dict):
            raise CouldNotMeasure("a workflow run entry is not an object")
        if r.get("head_sha") != sha:
            raise CouldNotMeasure(f"run {r.get('id')} has head_sha {r.get('head_sha')!r}, not {sha}")
        stamps.append(parse_ts(r.get("created_at"), f"run {r.get('id')} created_at"))
    return min(stamps), len(runs)


def judge(reviews, head_sha, first_seen, pr_author):
    """Return (passed, detail rows). Pure: no I/O."""
    latest = {}
    for idx, rv in enumerate(reviews):
        if not isinstance(rv, dict):
            raise CouldNotMeasure("a review entry is not an object")
        state = rv.get("state")
        if state not in DECISIVE:
            continue
        user = (rv.get("user") or {}).get("login")
        if not user:
            raise CouldNotMeasure(f"review {rv.get('id')} has no user login")
        ts = parse_ts(rv.get("submitted_at"), f"review {rv.get('id')} submitted_at")
        key = (ts, idx)
        if user not in latest or key >= latest[user][0]:
            latest[user] = (key, rv, ts)
    rows, passed = [], False
    for user in sorted(latest):
        _, rv, ts = latest[user]
        reasons = []
        if rv.get("state") != "APPROVED":
            reasons.append(f"latest decision is {rv.get('state')}")
        if rv.get("commit_id") != head_sha:
            reasons.append(f"commit_id {str(rv.get('commit_id'))[:12]} is not the head")
        if not ts > first_seen:
            reasons.append("submitted_at is not after head_first_seen")
        if user == pr_author:
            reasons.append("reviewer is the PR author")
        if rv.get("author_association") not in TRUSTED:
            reasons.append(f"author_association {rv.get('author_association')} is not trusted")
        counts = not reasons
        passed = passed or counts
        rows.append({"reviewer": user, "state": rv.get("state"),
                     "submitted_at": rv.get("submitted_at"), "counts": counts,
                     "why_not": reasons})
    return passed, rows


def retrigger(api, repo, sha, workflow, token, polls, interval):
    """Re-run the latest pull_request run of WORKFLOW for SHA, once it has finished.
    Returns the run id. A run still in progress cannot be re-run (the API refuses), so
    wait for it; a run that never finishes inside the budget is COULD NOT MEASURE."""
    import time
    url = (f"{api}/repos/{repo}/actions/workflows/{workflow}/runs"
           f"?head_sha={sha}&event=pull_request&per_page=1")
    for i in range(polls):
        data, _ = get(url, token)
        runs = data.get("workflow_runs") if isinstance(data, dict) else None
        if not isinstance(runs, list):
            raise CouldNotMeasure("the workflow runs payload carries no workflow_runs list")
        if not runs:
            raise CouldNotMeasure(f"no pull_request run of {workflow} for {sha}; nothing to re-run")
        run = runs[0]
        if run.get("head_sha") != sha:
            raise CouldNotMeasure(f"run {run.get('id')} is for {run.get('head_sha')!r}, not {sha}")
        print(f"run {run.get('id')} attempt {run.get('run_attempt')} status {run.get('status')}")
        if run.get("status") == "completed":
            get(f"{api}/repos/{repo}/actions/runs/{run['id']}/rerun", token, method="POST")
            return run["id"]
        if i + 1 < polls:
            time.sleep(interval)
    raise CouldNotMeasure(f"run {run.get('id')} did not complete within {polls} poll(s)")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", required=True)
    ap.add_argument("--pr")
    ap.add_argument("--head-sha", required=True)
    ap.add_argument("--retrigger", action="store_true")
    ap.add_argument("--workflow", default="approval-at-head.yml")
    ap.add_argument("--polls", type=int, default=40)
    ap.add_argument("--interval", type=float, default=15.0)
    args = ap.parse_args(argv)
    api = os.environ.get("GITHUB_API_URL", "https://api.github.com").rstrip("/")
    token = os.environ.get("GH_TOKEN", "")
    try:
        if not REPO_RE.match(args.repo):
            raise CouldNotMeasure(f"--repo {args.repo!r} is not OWNER/REPO")
        if args.retrigger:
            if not SHA40.match(args.head_sha):
                raise CouldNotMeasure(f"--head-sha {args.head_sha!r} is not a full 40-char lowercase sha")
            if not re.match(r"^[A-Za-z0-9_.-]+\.ya?ml$", args.workflow):
                raise CouldNotMeasure(f"--workflow {args.workflow!r} is not a workflow file name")
            rid = retrigger(api, args.repo, args.head_sha, args.workflow, token,
                            max(1, args.polls), args.interval)
            emit("RERUN_REQUESTED", run_id=rid, head_sha=args.head_sha)
            print(f"re-run requested for run {rid}; that suite's check is re-judged on live state.")
            return 0
        if not args.pr or not args.pr.isdigit():
            raise CouldNotMeasure(f"--pr {args.pr!r} is not a number")
        if not SHA40.match(args.head_sha):
            raise CouldNotMeasure(
                f"--head-sha {args.head_sha!r} is not a full 40-char lowercase sha. "
                "actions/runs answers 0 for an abbreviation with HTTP 200, so a short sha "
                "would read as never arrived")
        pr, _ = get(f"{api}/repos/{args.repo}/pulls/{args.pr}", token)
        live_head = ((pr or {}).get("head") or {}).get("sha") if isinstance(pr, dict) else None
        author = ((pr or {}).get("user") or {}).get("login") if isinstance(pr, dict) else None
        if not live_head or not author:
            raise CouldNotMeasure("the PR payload has no head.sha or user.login")
        if live_head != args.head_sha:
            emit("FAIL", reason="head moved", event_head=args.head_sha, live_head=live_head)
            print(f"FINDING: the PR head is now {live_head}, not {args.head_sha}. "
                  "This run judges a superseded sha; the run for the new head decides.")
            return 1
        first_seen, n_runs = head_first_seen(api, args.repo, args.head_sha, token)
        reviews = get_all(f"{api}/repos/{args.repo}/pulls/{args.pr}/reviews?per_page=100", token)
        passed, rows = judge(reviews, args.head_sha, first_seen, author)
    except CouldNotMeasure as exc:
        emit("COULD_NOT_MEASURE", reason=str(exc))
        print(f"COULD NOT MEASURE: {exc}", file=sys.stderr)
        return 2
    fs = first_seen.strftime("%Y-%m-%dT%H:%M:%SZ")
    emit("PASS" if passed else "FAIL", head_sha=args.head_sha, head_first_seen=fs,
         runs_read=n_runs, reviews_read=len(reviews), reviewers=rows)
    print(f"head {args.head_sha} first seen {fs} (earliest of {n_runs} run(s)); "
          f"{len(reviews)} review row(s), {len(rows)} reviewer(s) with a decision")
    for r in rows:
        mark = "COUNTS" if r["counts"] else "does not count: " + "; ".join(r["why_not"])
        print(f"  {r['reviewer']}: {r['state']} at {r['submitted_at']}: {mark}")
    if passed:
        print("PASS: an approval was given after the remote first saw this head.")
        return 0
    print("FINDING: no approval was given after the remote first saw this head. "
          "Re-approve at this head (an update-branch needs a fresh approval).")
    return 1


if __name__ == "__main__":
    sys.exit(main())
