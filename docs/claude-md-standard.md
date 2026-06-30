# CLAUDE.md authoring standard -- skyphusion-labs

A repo's CLAUDE.md is the contract a contributor (human or crew) works from WITHOUT reading all the
code. Calibrate to `the-hollow-grid/CLAUDE.md` (the exemplar). Required sections, in order:

1. `# CLAUDE.md` + one line: "Guidance for Claude Code (and the crew) working in this repo."
2. **What this is** -- 2-4 sentences: purpose, what it does, where it runs / deployed URL, current
   version (from package.json or latest release/tag).
3. **Constellation / ecosystem map** -- ONLY if part of a family (vivijure render repos; the MUD
   federation). Use the same ASCII map shared across the family so the whole map is visible from any
   one repo.
4. **Documentation map** -- bullet each `docs/` file with a one-line "what it covers"; state the rule:
   when a change touches an area, update the matching doc.
5. **Commands** -- the REAL toolchain commands (read package.json scripts / the actual build system).
   Mark the CI gate. Python repos: the real test/lint/build (pytest, ruff, docker build), not npm.
6. **Verifying changes** -- the repo's ACTUAL verify method (vitest; module conformance; live
   `wrangler dev` + assert on the structured event channel; pytest; a scripted WebSocket/HTTP smoke
   client). If there is no unit suite by design, say so and say how it IS verified.
7. **Architecture** -- the few load-bearing design facts that bite a contributor who does not know them.
8. **Conventions** -- repo-specific first, then the HOUSE block:
   - No em-dashes (U+2014) or en-dashes (U+2013) ANYWHERE. Use commas, semicolons, parentheses, or `--`.
   - Handle / username is `skyphusion`.
   - Minimal runtime deps; no framework / no build step beyond the language toolchain unless the repo
     genuinely needs one; justify any new dependency.
   - Workers repos: mirror every `wrangler` binding in a hand-authored `Env` interface (do not generate
     `worker-configuration.d.ts`).
   - `npm run typecheck` (or the repo's equivalent gate) must pass before pushing.
9. **Crew + identity** -- the `sudo -u <member> bash -lc '<ops>'` first-command ritual (own $HOME, own
   clone, own creds); a pointer to this repo's per-project memory; commits land under the member's own
   `skyphusion-<member>` identity, never Conrad's. (Conrad devs ONLY on his laptop, where his commits
   author as `Conrad Rockenhaus <conrad@skyphusion.org>` -- his real name kept, the in-house
   `@skyphusion.org` email; his name is never stripped and his history is never rewritten. On jello the
   `conrad` user is the god process and commits as `Mackaye <mackaye@skyphusion.org>`.)
10. **Commits & versioning** -- Conventional Commits (`feat(scope):` / `fix(scope):` / `docs:`), body
    explains the why; SemVer-style `0.MINOR.PATCH` while pre-1.0; a release commit bumps the version and
    adds a CHANGELOG entry.

## Hard rules

- VERIFY every claim against the REAL repo: package.json, wrangler.toml(.example), Dockerfile,
  requirements.txt, `.github/workflows/`, README, src/ layout. NO fabricated commands, scripts, or URLs.
  If you cannot confirm a command exists, do not list it.
- Reference `prism` (the repo was renamed FROM `skyphusion-llm-public`; the deployed worker stays
  `skyphusion-llm` at play.skyphusion.org). Fix any stale `skyphusion-llm-public` reference you find.
- NEVER put a secret value, token, or a private hostname/IP that must stay private into a CLAUDE.md.
  Infra repos: describe the safety invariants WITHOUT leaking the secrets they protect.
- Keep it tight. the-hollow-grid (~11KB) is the high end; most repos land 3-8KB. A generic templated
  file that does not match the repo is WORSE than none -- it misleads the crew.
