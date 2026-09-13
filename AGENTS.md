# AI Agent Guidelines — QFZZ

## Authorized Agents

- **GitHub Copilot**: Feature development, issue resolution. Targets `development` branch.
- **Geryon/OpenClaw**: Infrastructure, governance, batch operations.
- **Claude (Cowork/Code)**: Planning, code review, documentation.
- **Cursor**: Thin docs/CI/hygiene and Cloud Agent bootstrap. Prefer `cursor/<task>`.
- **Dependabot**: Automated dependency updates (opens against `development`).

## Branch Rules

- Never commit directly to `main`. Always use PRs.
- Target `development` for all feature work (live long-lived branch; there is no `develop`).
- Use conventional branch naming: `feat/`, `fix/`, `docs/`, `ci/`, `cursor/`.

## Cloud Agent bootstrap

- [`.cursor/environment.json`](.cursor/environment.json) — `install` verifies keeper files only (no `start`, no secrets).
- Do not put tokens, API keys, or credentials in env.json, docs, issues, commits, or logs.
- Local demo may need `GEMINI_API_KEY` / `GOOGLE_AI_API_KEY` from `.env.example`; those stay in the agent/runtime secret store, never in git.

## PR Labels

- `agent:copilot`, `agent:geryon`, `agent:claude`, `agent:dependabot`
- `safe-to-merge` — CI passes, no breaking changes, low-risk.

## CI Requirements

All PRs must pass configured status checks before merge. Hygiene (required files + committed-secret scan) is expected green; lint/test may still fail honestly on existing debt (see #101).

## File Restrictions

- Do not modify `.env` files or commit secrets.
- Do not delete governance files without human approval.
- Do not force-push to any protected branch.