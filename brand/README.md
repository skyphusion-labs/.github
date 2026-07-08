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
