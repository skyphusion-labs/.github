# Contributing to Skyphusion Labs

Thanks for your interest. This is the **org-wide default** for Skyphusion Labs repos. A repo
that ships its own `CONTRIBUTING.md` overrides this file; where a repo has none, this applies.

Our projects are labors of love, maintained as time allows. Response times on issues and PRs
may vary. If you find something useful and want to make it better, you are welcome here.

## Licensing of contributions (inbound = outbound)

By submitting a contribution (a pull request, patch, or any other work) you agree that your
contribution is licensed under the **same license as the project you are contributing to** (see
that repo's `LICENSE`). Most of our software is **AGPL-3.0-only**; a few repos are MIT, and some
documents carry their own license (for example a research paper under CC-BY-4.0). Match the
license of the repo and the file you are touching.

You also affirm that the contribution is **your own original work** (or appropriately licensed),
and that you have the right to contribute it under that license. Please do not paste code, text,
or diffs you do not have the rights to.

## Sign your work (Developer Certificate of Origin)

We use the [Developer Certificate of Origin](https://developercertificate.org/) (DCO) instead of
a CLA: no paperwork, no copyright assignment, just a per-commit affirmation that you wrote the
patch or otherwise have the right to submit it under the project's license.

Sign off every commit:

```bash
git commit -s
```

That appends a line to your commit message:

```
Signed-off-by: Your Name <your.email@example.com>
```

The name and email must be real and must match the commit author. By signing off you certify the
[DCO](https://developercertificate.org/) (reproduced there in full). Unsigned commits may be asked
to amend with `git commit --amend -s` (or `git rebase --signoff` for a series) before merge.

## House rules

- **No em-dashes (U+2014) or en-dashes (U+2013) anywhere** in source, comments, docs, or commit
  messages. Use commas, semicolons, parentheses, or a double hyphen (`--`).
- **Conventional Commits**: `fix(scope): ...`, `feat(scope): ...`, `docs: ...`, `ci: ...`. The
  body explains the *why*.
- Versioning is SemVer-style (PATCH for fixes, MINOR for features while pre-1.0). Release mechanics
  vary per repo; follow that repo's docs.
- Keep PRs focused. Larger feature work is best discussed in an issue first, so we can agree on the
  shape before you invest time.

## Pull requests

- Branch from the repo's default branch; CI must pass.
- The default branch is protected and changes land by review. Open the PR, keep it focused, and
  tag the maintainer.

## Code of conduct

Participation is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). Be decent to each other.

## Security

Please do **not** open a public issue for a security vulnerability. See
[SECURITY.md](SECURITY.md) for private reporting.
