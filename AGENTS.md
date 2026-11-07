# Agent instructions

This is a disposable CloudHop integration-test notes app, not a production service. Preserve api/ and web/ and use fictional data only.

## Validation
Run API tests from api/ with DATABASE_URL unset: `python -m pytest -q`. Run `npm ci && npm run build` from web/. Add regression tests for behavior changes. Never access production databases or deploy resources during reviews.

## PR review
After opening a ready PR, check whether the workflow or another agent already requested review for its current head. If not, post a top-level `@codex review` comment. After fixes, request again once per new head. Confirm the returned review references the current commit. A posted request, a successful request job, silence or a thumbs-up is not a formal approval. Request APPROVE only if the review passes and the integration supports it; otherwise report the limitation. Do not merge or bypass required CI and approvals.

## Nightly issues
A Codex app schedule runs daily at 22:00 Asia/Kolkata, separately from GitHub Actions. Read current code and open/closed issues plus active PRs. Inspect changes since the last completed review, then rotate through API validation, storage, external integration and frontend behavior. Verify findings safely and deduplicate before filing.

Every created issue must have `agent:codex` and an appropriate type (`bug`, `enhancement` or `security`). Include severity, pinned commit/line evidence, reproduction, expected/actual behavior, fix guidance and regression-test acceptance criteria for Claude. Report labeling failures. Follow SECURITY.md for sensitive findings. Record reviewed commit and coverage for the next run.
