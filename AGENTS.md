# Working Guidelines

- **Discuss before code changes:** suggest and discuss code changes first. Documentation-only changes may be made directly when they are clearly within the user's request. Reading files and discussing proposals do not require approval.
- **Simple changes:** implement the minimal change that meets the agreed requirements. Add complexity iteration by iteration as needs become clear.
- **Incremental changes:** always follow [docs/guides/implement-test-iterate.md](docs/guides/implement-test-iterate.md) for making changes.
- **Focused changes:** solve the agreed problem without unrelated refactoring or new dependencies.

## Definition of done

Before reporting a feature as complete:

1. Run the same commands configured in `.gitlab-ci.yml`.
2. Confirm every command passes.
3. If a check fails because of pre-existing code, do not claim CI readiness. Either fix it or update
   the CI scope and documentation deliberately.
4. Report the exact commands and results.

The maintained application is under `src/` and its tests are under `tests/`. The `inherited/`
application is a separate legacy application and is not included in maintained-application CI
checks unless its checks are passing.


## Coding practices

See the project documentation for the detailed guidance:

- [Good coding practices](docs/guides/good-coding-practices.md) for OOP, functions, naming, docstrings, and type hints.
- [Testing with pytest](docs/guides/pytest-testing.md) for test structure, test levels, and pytest usage.
- [Ruff linting and formatting](docs/guides/ruff-linter-formatter.md) for linting and formatting commands.
- [Type checking with mypy](docs/guides/mypy-type-checker.md) for static type-checking guidance.
- [GitHub/GitLab continuous integration](docs/guides/github-gitlab-continuous-integration.md) for the project’s continuous-integration checks.
