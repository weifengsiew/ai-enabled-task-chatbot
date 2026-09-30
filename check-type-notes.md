# Type-check notes

## Approved fixes

- assignment (two findings): annotate `Task.note` and `Task.day` as `str | None` in `src/bao/cli.py`, allowing strings after initialization with `None`.
- import-not-found / no-redef: import `TYPE_CHECKING` and use `if TYPE_CHECKING or __package__:` in each of these files:
  - `inherited/tasks.py`
  - `inherited/ui.py`
  - `inherited/command_handlers.py`
  - `inherited/bao.py`

Mypy follows the relative package imports. At runtime, `TYPE_CHECKING` is false, preserving the existing package and direct-script import paths. No type-error suppressions were added.

## Results

- `uv run mypy . > mypy-report.txt 2>&1`: success; report regenerated, down from 43 errors in 5 files to no issues in 13 source files.
- `uv run ruff check .`: all checks passed.
- `uv run pytest tests -q`: 6 passed.
- `uv run python -m pytest inherited/tests -q`: 13 passed.
- Inherited app launch checks: direct script and package execution both accepted `bye` and exited successfully, using temporary directories to isolate saved data.
- `git diff --check`: passed for the code fixes.

Existing mypy dependency changes in `pyproject.toml` and `uv.lock` were retained. No commit or push performed.
