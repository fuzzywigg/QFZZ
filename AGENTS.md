# AI Agent Guidelines — QFZZ

## Authorized Agents

- **GitHub Copilot**: Feature development, issue resolution. Targets `develop` branch.
- **Geryon/OpenClaw**: Infrastructure, governance, batch operations.
- **Claude (Cowork/Code)**: Planning, code review, documentation.
- **Dependabot**: Automated dependency updates.

## Branch Rules

- Never commit directly to `main`. Always use PRs.
- Target `develop` for all feature work.
- Use conventional branch naming: `feat/`, `fix/`, `docs/`, `ci/`.

## PR Labels

- `agent:copilot`, `agent:geryon`, `agent:claude`, `agent:dependabot`
- `safe-to-merge` — CI passes, no breaking changes, low-risk.

## CI Requirements

All PRs must pass configured status checks before merge.

## File Restrictions

- Do not modify `.env` files or commit secrets.
- Do not delete governance files without human approval.
- Do not force-push to any protected branch.