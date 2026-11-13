#!/usr/bin/env python3
"""Fixture builder and fixture API server for approval-at-head.test.sh (fc#2386).

  approval-at-head-fixtures.py mkcase DIR CASE   write DIR/routes.json for CASE
  approval-at-head-fixtures.py serve DIR PORTFILE  serve DIR/routes.json on 127.0.0.1

The server answers ONLY the exact path+query a route names, and 404s anything
else, so a checker that asks the wrong question (a short sha, a missing
per_page, a wrong PR) gets an error rather than a convenient answer. Every
request is appended to DIR/requests.log so the suite can assert what was asked.
"""
import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

REPO = "skyphusion-labs/pilot"
PR = 7
HEAD = "9a7690b9fbf603aaa35f988f647ae7ea6eedf2d1"
OLD = "0883d0d3c1a2b4e5f60718293a4b5c6d7e8f9012"
AUTHOR = "skyphusion-strummer"
FIRST_SEEN = "2026-11-12T12:00:00Z"


def run(i, created, sha=HEAD):
    return {"id": i, "head_sha": sha, "created_at": created}


def review(i, user, state, submitted, commit=HEAD, assoc="MEMBER"):
    return {"id": i, "user": {"login": user}, "state": state,
            "submitted_at": submitted, "commit_id": commit, "author_association": assoc}


PR_BODY = {"number": PR, "head": {"sha": HEAD}, "user": {"login": AUTHOR}}
RUNS_DEFAULT = [run(3, "2026-11-12T12:20:00Z"), run(2, "2026-11-12T12:05:00Z"),
                run(1, FIRST_SEEN)]

# Each case: reviews list, and optional overrides.
CASES = {
    # green: approval after the head first appeared
    "fresh": {"reviews": [review(1, "skyphusion-mackaye", "APPROVED", "2026-11-12T12:10:00Z")]},
    # red: approved the old head at 11:55, update-branch made HEAD at 12:00, and
    # GitHub re-pointed the review commit_id at HEAD (fc#1657). Only time tells.
    "stale-update-branch": {"reviews": [review(1, "skyphusion-mackaye", "APPROVED", "2026-11-12T11:55:00Z")]},
    "none": {"reviews": []},
    "comment-only": {"reviews": [review(1, "skyphusion-mackaye", "COMMENTED", "2026-11-12T12:10:00Z")]},
    # red: a fresh approval that was then dismissed reads DISMISSED in the API
    "dismissed": {"reviews": [review(1, "skyphusion-mackaye", "DISMISSED", "2026-11-12T12:10:00Z")]},
    # green: two reviewers, one stale, one fresh
    "two-one-fresh": {"reviews": [
        review(1, "skyphusion-rollins", "APPROVED", "2026-11-12T11:55:00Z"),
        review(2, "skyphusion-mackaye", "APPROVED", "2026-11-12T12:10:00Z")]},
    # red: two reviewers, both stale
    "two-both-stale": {"reviews": [
        review(1, "skyphusion-rollins", "APPROVED", "2026-11-12T11:50:00Z"),
        review(2, "skyphusion-mackaye", "APPROVED", "2026-11-12T11:55:00Z")]},
    # green: same reviewer, stale then fresh re-approval
    "reapproved": {"reviews": [
        review(1, "skyphusion-mackaye", "APPROVED", "2026-11-12T11:55:00Z"),
        review(2, "skyphusion-mackaye", "APPROVED", "2026-11-12T12:10:00Z")]},
    # red: fresh approval, then the same reviewer requested changes
    "approve-then-changes": {"reviews": [
        review(1, "skyphusion-mackaye", "APPROVED", "2026-11-12T12:10:00Z"),
        review(2, "skyphusion-mackaye", "CHANGES_REQUESTED", "2026-11-12T12:11:00Z")]},
    # clock skew, tolerance 0 and strictly-after
    "skew-before-3s": {"reviews": [review(1, "skyphusion-mackaye", "APPROVED", "2026-11-12T11:59:57Z")]},
    "skew-equal": {"reviews": [review(1, "skyphusion-mackaye", "APPROVED", FIRST_SEEN)]},
    "skew-after-3s": {"reviews": [review(1, "skyphusion-mackaye", "APPROVED", "2026-11-12T12:00:03Z")]},
    # red: fresh time but the reviewer was looking at the old head (stale page)
    "fresh-wrong-commit": {"reviews": [review(1, "skyphusion-mackaye", "APPROVED", "2026-11-12T12:10:00Z", commit=OLD)]},
    # red: fresh approval from a stranger
    "stranger": {"reviews": [review(1, "drive-by", "APPROVED", "2026-11-12T12:10:00Z", assoc="NONE")]},
    # red: zero runs is COULD NOT MEASURE
    "zero-runs": {"reviews": [review(1, "skyphusion-mackaye", "APPROVED", "2026-11-12T12:10:00Z")], "runs": []},
    # red: the head moved since the event
    "head-moved": {"reviews": [review(1, "skyphusion-mackaye", "APPROVED", "2026-11-12T12:10:00Z")],
                   "pr": {"number": PR, "head": {"sha": OLD}, "user": {"login": AUTHOR}}},
    # green ONLY if page 2 of runs is read: the earliest run is on page 2, and
    # page 1 alone would put first_seen at 12:30, after the 12:10 approval.
    "runs-paginated": {"reviews": [review(1, "skyphusion-mackaye", "APPROVED", "2026-11-12T12:10:00Z")],
                       "runs_pages": [[run(9, "2026-11-12T12:40:00Z"), run(8, "2026-11-12T12:30:00Z")],
                                      [run(1, FIRST_SEEN)]]},
    # green ONLY if page 2 of reviews is read
    "reviews-paginated": {"reviews_pages": [
        [review(1, "skyphusion-rollins", "APPROVED", "2026-11-12T11:55:00Z")],
        [review(2, "skyphusion-mackaye", "APPROVED", "2026-11-12T12:10:00Z")]]},
    # red: the reviews endpoint errors
    "reviews-500": {"reviews_status": 500},
    # red: a run whose head_sha is not the asked sha (the endpoint is exact; a
    # mismatch means the answer is not about this sha)
    "run-wrong-sha": {"reviews": [review(1, "skyphusion-mackaye", "APPROVED", "2026-11-12T12:10:00Z")],
                      "runs": [run(1, FIRST_SEEN, sha=OLD)]},
    # red: an unparseable timestamp is not silently skipped
    "bad-timestamp": {"reviews": [review(1, "skyphusion-mackaye", "APPROVED", "yesterday")]},
}


def wf_run(status, i=55, sha=HEAD, attempt=1):
    return {"id": i, "head_sha": sha, "status": status, "run_attempt": attempt}


# --retrigger cases: the review event re-runs the pull_request run (fc#2386).
RT_CASES = {
    "rt-completed": {"seq": [[wf_run("completed")]]},
    "rt-wait": {"seq": [[wf_run("in_progress")], [wf_run("completed")]]},
    "rt-never": {"seq": [[wf_run("in_progress")]]},
    "rt-none": {"seq": [[]]},
    "rt-wrong-sha": {"seq": [[wf_run("completed", sha=OLD)]]},
    "rt-refused": {"seq": [[wf_run("completed")]], "post_status": 403},
}


def mk_rt(d, name):
    c = RT_CASES[name]
    base = f"/repos/{REPO}"
    q = (f"{base}/actions/workflows/approval-at-head.yml/runs"
         f"?head_sha={HEAD}&event=pull_request&per_page=1")
    routes = {q: {"seq": [{"body": {"total_count": len(r), "workflow_runs": r}} for r in c["seq"]]},
              f"POST {base}/actions/runs/55/rerun": {"status": c.get("post_status", 201), "body": None}}
    with open(f"{d}/routes.json", "w") as fh:
        json.dump(routes, fh)


def mkcase(d, name):
    if name in RT_CASES:
        return mk_rt(d, name)
    c = CASES[name]
    base = f"/repos/{REPO}"
    runs_q = f"{base}/actions/runs?head_sha={HEAD}&per_page=100"
    rev_q = f"{base}/pulls/{PR}/reviews?per_page=100"
    routes = {f"{base}/pulls/{PR}": {"body": c.get("pr", PR_BODY)}}
    if "runs_pages" in c:
        p = c["runs_pages"]
        routes[runs_q] = {"body": {"total_count": 3, "workflow_runs": p[0]},
                          "next": runs_q + "&page=2"}
        routes[runs_q + "&page=2"] = {"body": {"total_count": 3, "workflow_runs": p[1]}}
    else:
        runs = c.get("runs", RUNS_DEFAULT)
        routes[runs_q] = {"body": {"total_count": len(runs), "workflow_runs": runs}}
    if "reviews_status" in c:
        routes[rev_q] = {"status": c["reviews_status"], "body": {"message": "boom"}}
    elif "reviews_pages" in c:
        p = c["reviews_pages"]
        routes[rev_q] = {"body": p[0], "next": rev_q + "&page=2"}
        routes[rev_q + "&page=2"] = {"body": p[1]}
    else:
        routes[rev_q] = {"body": c["reviews"]}
    with open(f"{d}/routes.json", "w") as fh:
        json.dump(routes, fh)


def serve(d, portfile):
    with open(f"{d}/routes.json") as fh:
        routes = json.load(fh)

    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_POST(self):
            self._answer("POST " + self.path)

        def do_GET(self):
            self._answer(self.path)

        def _answer(self, key):
            with open(f"{d}/requests.log", "a") as log:
                log.write(key + "\n")
            r = routes.get(key)
            if r is not None and "seq" in r:
                seq = r["seq"]
                r = seq.pop(0) if len(seq) > 1 else seq[0]
            if r is None:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'{"message":"Not Found"}')
                return
            self.send_response(r.get("status", 200))
            if "next" in r:
                host = self.headers.get("Host")
                self.send_header("Link", f'<http://{host}{r["next"]}>; rel="next"')
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            if r.get("body") is not None:
                self.wfile.write(json.dumps(r["body"]).encode())

    srv = HTTPServer(("127.0.0.1", 0), H)
    with open(portfile + ".tmp", "w") as fh:
        fh.write(str(srv.server_address[1]))
    import os
    os.replace(portfile + ".tmp", portfile)
    srv.serve_forever()


if __name__ == "__main__":
    if sys.argv[1] == "mkcase":
        mkcase(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "serve":
        serve(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "cases":
        print("\n".join(list(CASES) + list(RT_CASES)))
    else:
        sys.exit(2)
