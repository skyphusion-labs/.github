# OSS distribution channels

Where Skyphusion Labs ships public artifacts outside GitHub. **GitHub remains source of truth**; these channels are install shortcuts.

## npm (`@skyphusion` scope)

Create the [`@skyphusion` npm organization](https://www.npmjs.com/org/create) and add org secret **`NPM_TOKEN`** (Automation token with publish access) on `skyphusion-labs/.github` and each publishing repo.

| Package | Repo | Install | Published contents |
| --- | --- | --- | --- |
| [`@skyphusion/search-mcp`](https://www.npmjs.com/package/@skyphusion/search-mcp) | [search-mcp](https://github.com/skyphusion-labs/search-mcp) | `npm install @skyphusion/search-mcp` | Corpus sync CLIs (`search-mcp-sync`, `search-mcp-sync-run`), ask-widget assets |
| [`@skyphusion/hollow-grid-bot`](https://www.npmjs.com/package/@skyphusion/hollow-grid-bot) | [mud-bots](https://github.com/skyphusion-labs/mud-bots) | `npm install @skyphusion/hollow-grid-bot` | Hollow Grid AI player (`hollow-grid-bot` bin) |
| [`@skyphusion/sidvicious-exe`](https://www.npmjs.com/package/@skyphusion/sidvicious-exe) | [SidVicious_exe](https://github.com/skyphusion-labs/SidVicious_exe) | `npx @skyphusion/sidvicious-exe` | Discord roadie (`sidvicious` bin); search-worker stays deploy-from-git |

Release mechanics: bump `version` in the package manifest, tag GitHub Release `vX.Y.Z`, workflow publishes on release publish.

## PyPI

Org secret **`PYPI_API_TOKEN`** on publishing repos (pypi.org → Account settings → API tokens).

| Package | Repo | Install |
| --- | --- | --- |
| [`postern-client`](https://pypi.org/project/postern-client/) | [postern](https://github.com/skyphusion-labs/postern) | `pip install postern-client` |

## GHCR (container images)

GPU modules, bots, and fleet services publish to **`ghcr.io/skyphusion-labs/<image>:<tag>`** from their home repos (see each repo's release workflow). Examples:

- `ghcr.io/skyphusion-labs/mud-bots-hg`
- `ghcr.io/skyphusion-labs/vivijure-backend`
- `ghcr.io/skyphusion-labs/vivijure-local-12gb`

## Not on npm/PyPI (deploy from git)

Cloudflare Workers and full stacks (vivijure, prism, postern worker, the-hollow-grid, common-thread) deploy from a clone via `wrangler` / project runbooks. Use the repo README and `docs/DEPLOY.md`; npm/PyPI only cover CLI/library slices where that helps adopters.

## Adding a new channel

1. Add the package manifest (`package.json`, `pyproject.toml`, etc.) with `publishConfig.access: public` for scoped npm.
2. Add `.github/workflows/publish-*.yml` gated on GitHub Release + version match.
3. Document install path in the repo README.
4. Add a row to this file.
