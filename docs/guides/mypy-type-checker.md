# mypy Type Checker — Quick Guide

`mypy` statically checks Python type hints without running your code.

## Getting started

Add mypy as a development dependency:

```bash
uv add --dev mypy
```

Run it against a file, package, or source directory:

```bash
uv run mypy app.py
uv run mypy src/
uv run mypy -p mypackage
```

For stricter checking:

```bash
uv run mypy --strict src/
```

## Useful commands

```bash
uv run mypy src/                    # check source tree
uv run mypy --strict src/           # enable stricter checks
uv run mypy --check-untyped-defs src/
uv run mypy --python-version 3.12 src/
uv run mypy --show-error-codes src/
```

Minimal `pyproject.toml`:

```toml
[tool.mypy]
python_version = "3.12"
strict = true
show_error_codes = true
warn_unused_ignores = true
```

## Check findings

A typical finding:

```text
app.py:8: error: Argument 1 to "greet" has incompatible type "int"; expected "str"  [arg-type]
```

Read it as:

```text
file:line → problem → actual type → expected type → error code
```

If the inferred type is unclear, inspect it:

```python
value = {"count": 1}
reveal_type(value)  # dict[str, int]
```

## Implement fixes

Fix the mismatch where possible:

```python
def greet(name: str) -> str:
    return f"Hello {name}"


greet("Ada")  # OK
greet(42)  # error
```

Narrow optional values before using them:

```python
def length(value: str | None) -> int:
    if value is None:
        return 0
    return len(value)
```

For unavoidable legacy or third-party gaps, suppress only the specific error:

```python
result = legacy_api()  # type: ignore[no-untyped-call]
```

Then rerun:

```bash
uv run mypy src/
```

Repeat until the findings are resolved.

## References

- [mypy: Getting started](https://mypy.readthedocs.io/en/stable/getting_started.html)
- [mypy: Command line](https://mypy.readthedocs.io/en/stable/command_line.html)
- [mypy: Common issues](https://mypy.readthedocs.io/en/stable/common_issues.html)
- [uv: Running commands](https://docs.astral.sh/uv/concepts/projects/run/)
