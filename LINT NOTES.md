# Lint notes

## Approved fixes

- I001: sort CLI imports; remove `datetime` after replacing its only use.
- PIE810: combine the mark/unmark prefix checks into one `startswith` call.
- ISC004 (four findings): parenthesize intentionally joined expected-output strings; keep their contents unchanged.
- DTZ007 (three findings): construct the CLI deadline `time` directly; document and narrowly suppress the two intentional timezone-free parses in `inherited/parser.py`, preserving accepted inputs.

## Results

- `uv run ruff check . --output-format=full --output-file=ruff-report.txt`: all checks passed; report regenerated, down from 9 findings to 0 (including two documented DTZ007 exemptions).
- `uv run pytest`: 6 passed.
- `uv run python -m pytest inherited/tests`: 13 passed.
- `git diff --check`: passed.

Existing Ruff dependency changes in `pyproject.toml` and `uv.lock` were retained. No commit or push performed.
