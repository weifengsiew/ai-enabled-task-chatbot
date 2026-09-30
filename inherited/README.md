# Inherited bao

This directory is used only for **Stage R — Inherited code** on Day 2.

`bao.py` is deliberately awkward but working code. Do not copy its design into the application
you build in the rest of the repository.

### Test

From the repository root, add pytest as a development dependency if needed:

```bash
uv add --dev pytest
```

Run the tests for `inherited/bao.py`:

```bash
uv run python -m pytest inherited/tests
```

Using `python -m pytest` makes the repository root available for imports.

### Run

To start the inherited application:

```bash
uv run python inherited/bao.py
```

The tests describe behaviour that the refactor must preserve. Keep `bao.py` as the runnable entry
point while splitting responsibilities into the modules named on the course site.
