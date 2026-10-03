# Working Guidelines

- **Discuss before implementing:** suggest and discuss changes first. Edit files only after explicit user approval, such as "change approved." Reading files and discussing proposals do not require approval.
- **Start simple:** implement the simplest solution that meets the agreed requirements. Add complexity iteration by iteration as needs become clear.
- **Keep changes focused:** solve the agreed problem without unrelated refactoring or new dependencies.
- **Implement-test-iterate:** for new features and bug fixes, write or update tests before implementation when practical. Do not modify those tests merely to make the implementation pass. Make the smallest code change that satisfies the agreed requirements, and run the relevant tests after each coherent change. Ensure the CI workflow runs pytest, Ruff linting/formatting checks, and mypy. Recommend committing and pushing only after CI passes.

## Coding practices

See [Good Coding Practices](docs/good-coding-practices.md) for OOP, function, naming, docstring, and type-hint guidance.
