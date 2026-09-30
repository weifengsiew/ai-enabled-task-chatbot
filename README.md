# bao

`bao` is the command-line task tracker you will build during the AIAP 23a software engineering
bootcamp.

Start with the course site's **Get ready** page and follow one stage at a time.

Prepare the project with:

```bash
uv sync
uv run python --version
```

## src/bao/

The repository includes a small package under `src/bao/`. The `bao` command is already connected
to `src/bao/cli.py`, and the supplied code completes Stage 0. Start on the course site's Stage 0
page: run the program, inspect how the command reaches Python, and make sure the toolchain works
before adding Stage 1 behaviour.

### Test

From the repository root (the `bao` project directory), run the pytest tests for
`src/bao/cli.py`:

```bash
uv run pytest
```

This runs the tests in `tests/`. Add `-v` to display each test's name and result.

The tests cover valid and invalid commands, plus saving and reloading tasks.
They use temporary directories, so your saved tasks are not affected.

### Run 

From the repository root, start the application with:

```bash
uv run bao
```

## inherited/

The other supplied application under `inherited/` belongs to a separate Day 2 refactoring
exercise. It is not a starting point or reference design for your own `bao`.

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
