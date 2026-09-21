# Inherited bao

This directory is used only for **Stage R — Inherited code** on Day 2.

`bao.py` is deliberately awkward but working code. Do not copy its design into the application
you build in the rest of the repository. At the start of Stage R, run:

```bash
uv run pytest inherited/tests
uv run python inherited/bao.py
```

The tests describe behaviour that the refactor must preserve. Keep `bao.py` as the runnable entry
point while splitting responsibilities into the modules named on the course site.
