# bao

`bao` is a command-line task tracker built during the AIAP 23a software engineering bootcamp.

## Setup

The project uses Python 3.13 and `uv`:

```bash
uv sync
uv run python --version
```

## Run bao

From the repository root:

```bash
uv run bao
```

Tasks are persisted in `data/tasks.json`. The file and its parent directory are created when
tasks are first saved.

## Source layout

```text
src/bao/
├── __init__.py              # Package marker.
├── cli.py                   # Console entry point and interactive chat loop.
├── read_task_commands.py    # Command base class, dispatcher, registry, and read/control commands:
│                            # bye, list, due, and find.
├── add_task_commands.py     # Commands that create tasks:
│                            # todo, deadline, event, and recurring.
├── modify_task_commands.py  # Commands that modify tasks:
│                            # mark, unmark, note, and delete.
├── parser.py                # Shared parsing helpers for dates, times, and task numbers.
├── task.py                  # Task model classes and task formatting/serialization fields.
└── tasks.py                 # Task collection plus loading, saving, and JSON persistence helpers.
```

The main flow is:

```text
user input → cli.py → read_task_commands.py dispatcher
            → command parser → command execution → Tasks → data/tasks.json
```

## Supported commands

| Command | Purpose |
| --- | --- |
| `todo <description>` | Add a todo task. |
| `deadline <description> /by YYYY-MM-DD [HHMM]` | Add a deadline. |
| `event <description> /from YYYY-MM-DD HHMM /to YYYY-MM-DD HHMM` | Add an event. |
| `recurring <description> /every <rule>` | Add a recurring task. |
| `list` | List saved tasks. |
| `due YYYY-MM-DD [HHMM]` | Find deadlines due on a date or at a time. |
| `find <text>` | Search task descriptions. |
| `mark <number>` | Mark a task as done. |
| `unmark <number>` | Mark a task as incomplete. |
| `note <number> <note>` | Replace a task's note. |
| `delete <number>` | Delete a task. |
| `bye` | Exit the interactive session. |

## Test

Run the test suite from the repository root:

```bash
uv run pytest
```

Use `-v` to display each test name and result. Tests use temporary directories, so test data does
not affect your saved tasks.

## Quality checks

Run the same checks used while developing the package:

```bash
uv run ruff check src
uv run ruff format --check src
uv run mypy src
```

## Course stages

Start with the course site's **Get ready** page and follow one stage at a time. The supplied code
completes Stage 0: run the program, inspect how the command reaches Python, and verify that the
toolchain works before adding Stage 1 behaviour.

## inherited/

The other supplied application under `inherited/` belongs to a separate Day 2 refactoring
exercise. It is not a starting point or reference design for this `bao` package.

To test it:

```bash
uv run python -m pytest inherited/tests
```

To run it:

```bash
uv run python inherited/bao.py
```
