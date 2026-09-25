# CLAUDE.md

Guidance for Claude Code (and the crew) working in this repo.

## What this is

`skyphusion-labs/.github`, the org meta-repo. Three jobs in one repo:

1. **Org-wide community health defaults.** `SECURITY.md`, `CONTRIBUTING.md`, and
   `CODE_OF_CONDUCT.md` here are GitHub's documented fallback: any repo in the org without its
   own copy of one of these files inherits this one. Editing one of these three changes the
   answer for every repo in `skyphusion-labs` that has not overridden it, not just this repo.
2. **The org profile Pages site**, `github.skyphusion.org` (`CNAME`), built by
   `.github/workflows/pages.yml` from `index.md` (which pulls in `profile/README.md`, the text
   GitHub also renders as the org's profile card). This is a public page; a careless edit here
   is a public change.
3. **The brand asset toolkit** (`brand/`): generates and uploads GitHub social-preview images
   and the X banner, and keeps repo topics / About metadata in sync with `brand/topics.json` /
   `brand/seo-metadata.json` (checked by `oss-discoverability-drift.yml`, which fails a PR when
   the live repo metadata has drifted from those catalog files).

`.github/dependabot.yml` here is this repo's OWN Dependabot config (github-actions + the
`brand/` npm deps); it is not inherited by other repos. It documents the org-wide Dependabot
shape (see its header comment) but each repo carries its own copy.

## Documentation map

- `docs/claude-md-standard.md` -- the authoring standard every other repo's `CLAUDE.md` is
  written against; calibrate to `the-hollow-grid/CLAUDE.md` as the exemplar.
- `brand/README.md` -- how to regenerate and upload social-preview / banner assets.
- `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` -- the org-wide fallbacks described
  above.

## Commands

- Regenerate brand assets: `cd brand && python3 generate.py` (Python, no deps beyond stdlib +
  Pillow-class tooling; check `generate.py` itself before assuming a package).
- Upload social previews (one-time browser login, then batch): `cd brand && npm install && npx
  playwright install chromium && node upload-via-ui.mjs --login`, then `node upload-via-ui.mjs`
  (GitHub has no public API for repo social-preview images).
- `brand/update-topics.sh` / `brand/apply-seo-metadata.sh` / `brand/check-catalog-coverage.sh`
  apply `topics.json` / `seo-metadata.json` to live repos via the GitHub API.

## Verifying changes

- `pages.yml`: push to `main` builds and deploys the Jekyll site; check the Pages build log and
  that `github.skyphusion.org` actually serves the change.
- `oss-discoverability-drift.yml`: gates any PR touching `brand/topics.json`,
  `brand/seo-metadata.json`, or the apply scripts against live repo state; a red run means a
  catalog file and GitHub's actual topics/About text disagree.
- `coverage.yml` is the org's required-check placeholder (see `docs/claude-md-standard.md`'s
  aviation-grade note); this repo has no root `package.json` or `go.mod`, so it runs the
  no-manifest passthrough, not real coverage.
- `corpus-notify.yml` fires a `repository_dispatch` at `search-mcp` on merge to `main` so its
  search corpus refreshes immediately instead of waiting for its own daily schedule; it is not
  a required check and never blocks this repo's CI.

## Note on `docs/claude-md-standard.md`

Its "Crew + identity" required section (point 9) still describes a single `conrad` unix
account as "the god process" that commits as `Mackaye <mackaye@skyphusion.org>`. That is stale:
there is no `mackaye` unix account on the current laptop-based crew seat model, each crew
member (including Mackaye) runs as its own unix account, wrapped
`sudo -n -H -u <member> bash -lc`. The exemplar this doc points to, `the-hollow-grid/CLAUDE.md`,
does not carry a "Crew + identity" section at all, which suggests current practice has already
moved to leaving that doctrine in the injected global files rather than duplicating it per
repo. Left unedited here: fixing the mechanics or dropping the section is a house-policy call
this repo's own standard should make deliberately, not a drive-by in an unrelated sweep.
