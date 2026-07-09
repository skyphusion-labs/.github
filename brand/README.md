# Skyphusion Labs brand assets

Social preview images for GitHub repo sharing and the @skyphusion X profile banner.

## Layout

- **GitHub social preview:** 1280×640 PNG (2:1). Applied per repo in GitHub Settings → Social preview. There is no public REST API; use `upload-via-ui.mjs` (Playwright) after a one-time `--login`.
- **X profile banner:** 1500×500 PNG. Upload manually in X profile settings.

Brand mark: fusion-rising icon from `assets/logo-icon.svg` (same as skyphusion.org).

## Regenerate

```bash
cd brand
python3 generate.py
```

Outputs land in `output/social-preview/` and `output/x-banner/`.

## Upload to GitHub

GitHub does not expose a public API for social preview images. Use the Playwright uploader (one-time browser login, then batch upload):

```bash
npm install
npx playwright install chromium
node upload-via-ui.mjs --login    # once: log into GitHub in the opened window
node upload-via-ui.mjs            # uploads every PNG in output/social-preview/
```

Single repo: `node upload-via-ui.mjs --repo skyphusion-labs/vivijure`

The legacy `upload-social-previews.sh` script is kept for reference but GitHub returns 404 on that REST path.

## Repo catalog

Edit `repos.json` to change taglines, accent colors, motif, or chip text per repo, then regenerate and re-upload.

## Repository topics (OSS discoverability)

GitHub [repository topics](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/classifying-your-repository-with-topics) are the org's public category tags. They drive topic search, related-repo discovery, and the "About" chips on each repo page. GitHub allows **at most 20 topics per repo**.

The canonical topic set for every **public** `skyphusion-labs` repo lives in `topics.json`, alongside `repos.json`. Each entry has:

| Field | Purpose |
|-------|---------|
| `owner` / `repo` | GitHub slug (`skyphusion-labs/vivijure`) |
| `family` | Constellation grouping for batch updates (`vivijure`, `hollow-grid`, `postern`, `sites`, `infra`, `org`, …) |
| `topics` | Sorted topic list (1–20). Include both **product family** tags (`vivijure`, `mud`, `postern`) and **stack** tags (`cloudflare-workers`, `typescript`, `agpl`). |

### Apply or verify

Prereqs: `gh` authenticated with org admin/repo scope, `jq` installed.

```bash
cd brand
chmod +x update-topics.sh

./update-topics.sh --dry-run          # show planned changes only
./update-topics.sh                      # push catalog -> GitHub for all public repos
./update-topics.sh --check              # CI/drift gate: exit 1 if live != catalog
./update-topics.sh --repo vivijure      # single repo
./update-topics.sh --family vivijure    # whole constellation
```

The script uses `PUT /repos/{owner}/{repo}/topics` (full replace). Always edit `topics.json` first, then run `--dry-run` before applying.

### When to update

- **New public repo:** add a row to `topics.json` (and `repos.json` if it gets a social preview) before or right after the public flip.
- **New capability shipped:** add stack or feature topics if there is room under the 20-topic cap.
- **Constellation rename:** update the family tag across sibling repos in one `--family` pass.

Topic conventions (org-wide):

- Constellation anchors: `vivijure`, `vivijure-module`, `the-hollow-grid`, `hollow-grid`, `postern`, `prism`, `common-thread`, `search-mcp`.
- House stack: `cloudflare-workers`, `self-hosted`, `agpl`, `open-source`, `typescript` / `python` / `golang` as appropriate.
- GPU satellites: `runpod`, `cuda`, `gpu`, plus model-specific tags (`sdxl`, `ltx-video`, `real-esrgan`, …).
- Do not exceed 20 topics; prefer discoverability over exhaustiveness.
