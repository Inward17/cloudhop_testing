# Security policy

This app is an unauthenticated deployment test fixture. Use fictional notes in isolated test infrastructure; do not store personal data, credentials or confidential content. Do not assume its current configuration is suitable for public production use.

Report vulnerabilities through GitHub private vulnerability reporting if available, otherwise obtain a private channel from Inward17. Do not publish sensitive details or copy private repository code into public issues or repositories.

Review SQL parameterization, input validation, cross-origin access, frontend rendering, secret handling and deployment boundaries. Use mocked services or disposable local resources, never production data.

For a PR whose visibility is appropriate, agents may request review with a top-level `@codex review` comment following AGENTS.md. Keep undisclosed vulnerability evidence in the approved private channel. Codex review does not replace required CI or formal approvals, and does not authorize merging or deployment.
