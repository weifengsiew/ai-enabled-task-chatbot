# Implement–Test–Iterate

1. Define the user story: "As a [who], I want [what], so that [why]."
2. Define the acceptance examples: "Given [context of system], when user [performs action], then [expected response of system]". 
3. Get approval for user story and acceptance examples. Use it to write or update tests, following the [pytest testing guide](pytest-testing.md).
4. Implement the smallest change using the project's [good coding practices](good-coding-practices.md), then run full checks using the [CI guide](github-actions-ci.md): [pytest](pytest-testing.md), [Ruff](ruff-linter-formatter.md), and [mypy](mypy-type-checker.md).
5. Recommend committing and pushing only after all checks pass, using the [CI guide](github-actions-ci.md) to confirm the shared pipeline result.
6. Document: where the code changes live? CI check results?
