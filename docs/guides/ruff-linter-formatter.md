# Ruff: Linting and Formatting

- **Ruff:** a fast Python linter and formatter written in Rust.
- **Linter:** run with `uv run ruff check`.
- **Formatter:** run with `uv run ruff format`.

This guide assumes a uv-managed project and Ruff's default rules, without custom rule selection or preview mode. Defaults can change between versions; see the [default rule reference](https://docs.astral.sh/ruff/default-rules/).

## What does each command do?

| | `uv run ruff check` | `uv run ruff format` |
| --- | --- | --- |
| Examines | Code constructs against enabled lint rules: unused imports, undefined names, suspicious conditions, and other potential mistakes. | The presentation of code: indentation, spaces, quotes, line breaks, and trailing commas. |
| Produces | Findings with a rule code, location, and explanation. | Consistently formatted source files. |
| Changes files | Applies available safe fixes when you add `--fix`. | Rewrites layout by default; `--check` only reports whether formatting would change. |
| Example | Flags `print(total)` if `total` is undefined. | Changes `items=[1,2]` to `items = [1, 2]`. |

- A file can pass linting but still need formatting, or pass formatting checks but still have lint violations. `uv run ruff check` checks code against lint rules; `uv run ruff format` standardizes its layout. The commands are complementary. Run both.

## Top commands

Run from the project root; `.` means the current directory. Replace it with a file or directory to narrow the scope.

| Command | Purpose |
| --- | --- |
| `uv run ruff check .` | Report lint violations without editing files. |
| `uv run ruff check --fix .` | Apply available safe fixes; report remaining issues. |
| `uv run ruff check --diff .` | Preview fixes as a diff without writing changes. |
| `uv run ruff check --watch .` | Recheck when files change. |
| `uv run ruff format .` | Format files in place. |
| `uv run ruff format --check .` | Check formatting without editing; useful in CI. |
| `uv run ruff format --diff .` | Preview formatting changes. |
| `uv run ruff rule F401` | Explain a rule (`F401` = unused import). |
| `uv run ruff check --help` | Show lint options. |

## Generate a linter report

```bash
# Human-readable report, without changing source files
uv run ruff check . --no-fix --output-format full --output-file ruff-report.txt

# Structured report for scripts or other tools
uv run ruff check . --no-fix --output-format json --output-file ruff-report.json
```

- Reports include findings from the enabled rules and files Ruff scans; they are not a record of previously fixed issues.

## Examples of linter findings

All six examples use default rules. Fix availability can depend on context and configuration.

### Can find and automatically fix

| Rule / problem type | Example finding | Automatic fix |
| --- | --- | --- |
| [F401](https://docs.astral.sh/ruff/rules/unused-import/) — unused dependency | `import math` in a normal module that never uses it. | `--fix` removes the import. `__init__.py` has special handling. |
| [F541](https://docs.astral.sh/ruff/rules/f-string-missing-placeholders/) — unnecessary string syntax | `message = f"Ready"` has no interpolation. | `--fix` changes it to `message = "Ready"`. |
| [F601](https://docs.astral.sh/ruff/rules/multi-value-repeated-key-literal/) — overwritten dictionary value | `settings = {"timeout": 10, "timeout": 20}` repeats a key. | `--fix --unsafe-fixes` removes the earlier entry, preserving the effective value `20`. Review whether that was intended. |

### Can find but cannot automatically fix

| Rule | Example finding | Manual resolution |
| --- | --- | --- |
| [F821](https://docs.astral.sh/ruff/rules/undefined-name/) | `print(total)` when `total` has never been defined. | Define or import the name, or correct a typo; Ruff cannot infer the intended value. |
| [E722](https://docs.astral.sh/ruff/rules/bare-except/) | `except:` catches every exception, including system exits and keyboard interrupts. | Choose the exception types the handler should catch. |
| [F634](https://docs.astral.sh/ruff/rules/if-tuple/) | `if (False,):` tests a nonempty tuple, which is always truthy; the branch runs. | Correct the condition; Ruff cannot infer the intended logic. |

## Setup

- **Install:** `uv add --dev ruff` adds Ruff as a development dependency. `uv run` runs it from the project environment.
- **Configuration:** defaults need no configuration. Ruff automatically reads settings from `pyproject.toml`, `ruff.toml`, or `.ruff.toml`. Add `--isolated` to ignore configuration files and use built-in defaults.

## Workflow

Run from the project root. Without a path, Ruff scans the current working directory recursively; `.` makes that explicit. Use `src/` or a filename to narrow the scan. Configuration and ignore files such as `.gitignore` determine which files are included or skipped.

- **Inspect the scope:** `uv run ruff check . --show-files` lists the files Ruff will check.
- **Locally:** run `uv run ruff check --fix .`, then `uv run ruff format .`, and review changes.
- **In CI:** run `uv run ruff check .` and `uv run ruff format --check .`; either fails when issues remain.
- **Unsafe fixes:** `--unsafe-fixes` opts into additional fixes that may change behavior; review them carefully.

Sources: [Requested guide](https://pydevtools.com/handbook/explanation/ruff-complete-guide/), [Ruff linter](https://docs.astral.sh/ruff/linter/), [Ruff formatter](https://docs.astral.sh/ruff/formatter/), [CLI reference](https://docs.astral.sh/ruff/configuration/#full-command-line-interface).
