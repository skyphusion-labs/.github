# Security policy

This is the **org-wide default** for Skyphusion Labs. A repo that ships its own `SECURITY.md`
overrides this file; where a repo has none, this applies.

## Supported versions

Our projects are rolling, single-`main`-branch efforts. Only the latest release (or the current
`main`) receives security fixes. If you are running an older revision, upgrade to the newest
release to pick them up.

## Reporting a vulnerability

Please do **not** file a public GitHub issue for security problems.

Report it privately through GitHub's private vulnerability reporting: open the repository's
**Security** tab and click **"Report a vulnerability"**. This creates a private advisory visible
only to you and the maintainers. If that option is not available on a given repo, email
**security@skyphusion.org** instead (do not disclose details in a public issue).

Please include:

- A description of the issue and its impact.
- Steps to reproduce, including a minimal example if possible.
- The affected version (release, tag, or commit SHA if known).
- Any suggestions for remediation.

Reports will be acknowledged within a reasonable window (target: 5 business days). Time-sensitive
issues should say so. Please allow up to 90 days for a coordinated fix before public disclosure.

## Scope of reports

Security reports should concern our own code and its runtime. The security posture of upstream
model weights or third-party libraries themselves should be reported to their respective projects
(beyond how our code invokes them). Please do not send code, diffs, or excerpts you do not have
the rights to share.
