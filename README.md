# bao

`bao` is the command-line task tracker you will build during the AIAP 23a software engineering
bootcamp.

Start with the course site's **Get ready** page and follow one stage at a time.

Prepare the project with:

```bash
uv sync
uv run python --version
```

The repository includes a small package under `src/bao/`. The `bao` command is already connected
to `src/bao/cli.py`, and the supplied code completes Stage 0. Start on the course site's Stage 0
page: run the program, inspect how the command reaches Python, and make sure the toolchain works
before adding Stage 1 behaviour.

The other supplied application under `inherited/` belongs to a separate Day 2 refactoring
exercise. It is not a starting point or reference design for your own `bao`.
