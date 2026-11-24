# AGENTS.md authoring standard -- skyphusion-labs

A public repo's `AGENTS.md` is the guide for any coding agent and any contributor.
`CLAUDE.md` is a short pointer to `AGENTS.md` only. Do not put private estate ops in either file.

Calibrate to a current public `AGENTS.md` in the same family (for example `hollow-grid-py/AGENTS.md`
or `pagefeather/AGENTS.md`). Required sections, in order:

1. `# <repo-name>` plus one line: "This file is the guide for any coding agent and any contributor. Follow it."
2. **What this project is** -- 2-4 short sentences: purpose, where it runs or the deployed URL, and the
   current version when the repo has one.
3. **Constellation / ecosystem map** -- ONLY if the repo is part of a family (vivijure render repos;
   the MUD federation). Use the same ASCII map shared across that family.
4. **Documentation map** -- bullet each `docs/` file with one line on what it covers. State the rule:
   when a change touches an area, update the matching doc.
5. **Commands** -- the real toolchain commands from `package.json` scripts or the real build system.
   Mark the CI gate. Python repos: pytest, ruff, docker build, or the real test and lint commands.
6. **Verifying changes** -- the repo's actual verify method. If there is no unit suite by design, say so
   and say how the repo is verified.
7. **Architecture** -- the few load-bearing design facts a new contributor needs.
8. **Conventions** -- repo-specific first, then the house block:
   - Write Simplified Technical English. Short sentences. One idea per sentence. Active present tense.
   - No em dashes (U+2014) or en dashes (U+2013) anywhere. Use commas, semicolons, parentheses, or `--`.
   - Handle / username is `skyphusion`.
   - Minimal runtime deps. No framework or build step beyond the language toolchain unless the repo
     needs one. Justify any new dependency.
   - Workers repos: mirror every `wrangler` binding in a hand-authored `Env` interface. Do not generate
     `worker-configuration.d.ts`.
   - `npm run typecheck` (or the repo's equivalent gate) must pass before pushing.
9. **Commits and versioning** -- Conventional Commits (`feat(scope):` / `fix(scope):` / `docs:`). The
   body explains why. SemVer-style `0.MINOR.PATCH` while pre-1.0. A release commit bumps the version
   and adds a CHANGELOG entry.

## CLAUDE.md stub

Keep `CLAUDE.md` to two lines that point at `AGENTS.md`. Do not duplicate the guide. Example:

```markdown
# <repo-name>

The project's agent guide is [AGENTS.md](AGENTS.md), which every agent (Claude included) follows.
```

## Hard rules

- VERIFY every claim against the real repo: package.json, wrangler.toml(.example), Dockerfile,
  requirements.txt, `.github/workflows/`, README, src layout. Do not invent commands, scripts, or URLs.
  If you cannot confirm a command exists, do not list it.
- Reference `prism` (the repo was renamed FROM `skyphusion-llm-public`; the deployed worker stays
  `skyphusion-llm` at play.skyphusion.org). Fix any stale `skyphusion-llm-public` reference you find.
- NEVER put a secret value, token, or a private hostname or IP that must stay private into `AGENTS.md`
  or `CLAUDE.md`. Infra repos: describe safety invariants without leaking the secrets they protect.
- Keep the public guide about the public repo only. Do not document crew host rituals, laptop seat
  rules, escrow paths, or private memory pointers here. Those live in private estate docs.
- Keep it tight. Most repos land 3-8KB. A generic templated file that does not match the repo is worse
  than none. It misleads contributors.
