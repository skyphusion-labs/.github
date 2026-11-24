# skyphusion-labs/.github

This file is the guide for any coding agent and any contributor. Follow it.

## What this repo is

This is the `skyphusion-labs/.github` meta repo. It has three public jobs.

`SECURITY.md`, `CONTRIBUTING.md`, and `CODE_OF_CONDUCT.md` are the org fallback files. A repo with no file of its own inherits the copy here. An edit here changes that answer for every such repo.

The profile site is https://github.skyphusion.org. [`.github/workflows/pages.yml`](.github/workflows/pages.yml) builds it from `index.md`. `index.md` includes `profile/README.md`. GitHub also shows that file as the org profile. The page is public.

`brand/` holds social-preview images and the topic catalogs. [`.github/workflows/oss-discoverability-drift.yml`](.github/workflows/oss-discoverability-drift.yml) fails when live repo metadata drifts from those catalogs. Read [brand/README.md](brand/README.md).

`.github/dependabot.yml` configures Dependabot for this repo only. Other repos do not inherit that file.

## Checks this repo runs

Workflows live in `.github/workflows/`. This tree has no job whose name is `ci`. Do not add an empty job just to invent that name. `coverage.yml` is the coverage check. This repo has no root `package.json` and no `go.mod`, so that job takes the no-manifest path.

The approval gate is `.github/actions/approval-at-head/`. Callers pin that action by a full commit SHA. A change on `main` does nothing until those callers pin the new SHA. The gate passes only after an approval lands on the current pull request head. The test is `bash .github/scripts/tests/approval-at-head.test.sh`. [`.github/workflows/approval-at-head-test.yml`](.github/workflows/approval-at-head-test.yml) runs it. The test needs no token.

`main` takes changes through a pull request. Do not force-push `main`.

## Brand commands

Read [brand/README.md](brand/README.md) before you regenerate images. `brand/update-topics.sh` applies `brand/topics.json`. `brand/apply-seo-metadata.sh` applies `brand/seo-metadata.json`. `brand/check-catalog-coverage.sh` checks that the catalogs cover the repos.

## Docs

Write Simplified Technical English. Use short sentences. Use one idea per sentence. Use the active present tense. Use plain words. Use the same word every time.

Do not use an em dash (U+2014). Do not use an en dash (U+2013). Use a comma, a semicolon, parentheses, or two hyphens (`--`).

State the limit next to the capability. Do not turn a measured result into a promise.

Keep this guide about the public repo only. Do not document internal operator process here.

## Safety

Do not put a secret in a tracked file, a log, or an issue. Treat a profile edit as a public change. Treat a fallback-file edit as an org-wide change.
