# Refactor Notes

## Existing commands in `bao.py`

All 13 commands are handled inside `run()`. The table follows their existing order.

| Command | Boolean condition | Syntax / example | Purpose |
|---|---|---|---|
| `bye` | `line == "bye"` | `bye` | Exit the program. |
| `list` | `line == "list"` | `list` | Display all tasks and their notes. |
| `todo` | `line.startswith("todo ")` | `todo buy milk` | Add a to-do task. |
| `deadline` | `line.startswith("deadline")` | `deadline submit report /by 2026-10-01 1800` | Add a deadline; time is optional. |
| `event` | `line.startswith("event")` | `event meeting /from Monday 2pm /to Monday 3pm` | Add an event; start and end are stored as text. |
| `recurring` | `line.startswith("recurring")` | `recurring exercise /every week` | Add a recurring task; interval is stored as text. |
| `mark` | `line.startswith("mark") or line.startswith("unmark")` | `mark 1` | Mark a task as completed. |
| `unmark` | Same shared condition as `mark` | `unmark 1` | Mark a task as incomplete. |
| `note` | `line.startswith("note")` | `note 1 bring documents` | Set or replace a task’s note. |
| `delete` | `line.startswith("delete")` | `delete 1` | Remove one task. |
| `clear` | `line == "clear"` | `clear` | Remove all completed tasks. |
| `find` | `line.startswith("find")` | `find report` | Search descriptions by case-insensitive substring. |
| `due` | `line.startswith("due")` | `due 2026-10-01` | Show deadline tasks due on that date. |

Before these conditions, `if not line.strip():` handles empty or whitespace-only input. The final `else:` handles unrecognized input.

Task numbers start at 1. Every command that changes tasks immediately saves them.

`bye`, `list`, and `clear` require exact matches. `todo` requires a following space. The remaining commands use loose `startswith(...)` checks.

## refactor step 1

Extract each branch into a function using a consistent `handle_<command>` naming pattern.

Move these functions into `command_handlers.py`. Keep `run()` in `bao.py` to coordinate the input loop and call the handlers.

| Boolean condition | Suggested function |
|---|---|
| `not line.strip()` | `handle_empty_input()` |
| `line == "bye"` | `handle_bye()` |
| `line == "list"` | `handle_list()` |
| `line.startswith("todo ")` | `handle_todo()` |
| `line.startswith("deadline")` | `handle_deadline()` |
| `line.startswith("event")` | `handle_event()` |
| `line.startswith("recurring")` | `handle_recurring()` |
| `line.startswith("mark") or line.startswith("unmark")` | `handle_mark_unmark()` |
| `line.startswith("note")` | `handle_note()` |
| `line.startswith("delete")` | `handle_delete()` |
| `line == "clear"` | `handle_clear()` |
| `line.startswith("find")` | `handle_find()` |
| `line.startswith("due")` | `handle_due()` |
| Final `else` | `handle_unknown_command()` |

`handle_mark_unmark()` covers both marking and unmarking because they currently share one branch.

A handler’s `return` only exits that handler. `run()` must still handle exiting after `bye` and continuing the input loop after invalid input.

### Step 1 results

Extracted handlers into `command_handlers.py`; `bao.py` retains loading, command routing, and the input loop.

- `uv run python -m pytest inherited/tests`: **13 passed** on rerun; supplied tests unchanged.
- Earlier comparisons matched the original output and saved bytes across five sessions, using both script and module entry points.

| Observation | Before | After |
|---|---|---|
| Largest function | `run()`: 247 lines | `handle_deadline()`: 47 lines |
| `run()` size | 247 lines | 46 lines |
| Module-level mutable values | 1 (`TASKS`) | 1 (`TASKS`) |

Sizes span `def` through the final statement, including docstrings and blank lines, across both modules. The immutable `DATA_FILE` path is excluded from the mutable-value count. These are observations, not targets.

Next: separate `ui`, `parser`, `tasklist`, and `storage`, and remove duplicated save logic.
