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

## refactor step 2

Review the functions in `command_handlers.py`, prioritizing those that are long or difficult to understand. Add comments identifying which area owns each logical block, using these responsibility definitions:

- `ui` owns the conversation and displayed messages.
- `parser` turns input into a command or a useful input error.
- `tasklist` owns task-list operations.
- `storage` loads and saves task data.

Where a block mixes responsibilities, identify each responsibility and explain where they overlap.

This step adds comments only to document the current code and guide later separation. Do not do anything else.

### Step 2 results

Added comments to `command_handlers.py` identifying `ui`, `parser`, `tasklist`, and `storage` responsibilities, including blocks where responsibilities overlap. Existing annotations in `handle_list()` were preserved.

Only comments were added. All original code lines were preserved, and the Python AST was unchanged.

### Step 3 discussion

- Extracting handlers shortened `run()`, but individual handlers still combine input parsing, task operations, displayed messages, and saving.
- Input validation and error display are closely coupled: a handler detects invalid input and immediately prints a message.
- Checking whether a task number is an integer belongs to `parser`; checking whether that task exists belongs to `tasklist`.
- Date conversion serves different responsibilities: interpreting user input belongs to `parser`, selecting deadlines belongs to `tasklist`, and formatting dates for display belongs to `ui`.
- The same two-line save block appears in eight handlers, making storage a clear first extraction.

## refactor step 3

Extract the duplicated two-line save block into `save_tasks(tasks, data_file)` in `storage.py`. Replace the block in all eight handlers with calls to this function.

Preserve directory creation, save timing, and JSON format. Run the supplied tests without modifying them.

### Step 3 results

Extracted `save_tasks(tasks, data_file)` into `storage.py` and replaced the duplicated save block in all eight handlers with calls to it.

- Directory creation and JSON serialization now have one implementation. The `json` import moved from `command_handlers.py` to `storage.py`.
- Handlers still decide when to save; `storage.py` owns how task data is written. Save timing, directory creation, and JSON format are unchanged.
- Loading remains in `bao.py`, so the storage responsibility is only partly separated. Handlers still combine parser, tasklist, and UI responsibilities.
- `uv run python -m pytest inherited/tests`: **13 passed**; supplied tests unchanged.
- Standalone script execution and exact saved JSON were also verified.

## refactor step 4

Extract file loading from `run()` in `bao.py` into `load_tasks(data_file: Path) -> list[dict[str, Any]]` in `storage.py`.

The function checks whether the file exists, reads and decodes its JSON, and returns the task data. A missing file returns an empty list. Read and JSON decoding errors propagate to `bao.py`, which handles them and displays the existing error message.

`run()` clears `TASKS` and extends it with the returned data. This places file access in `storage.py` while keeping task-list state and conversation handling in the caller.

Preserve existing behavior and verify it with the supplied tests.

### Step 4 results

- Extracted `load_tasks()` into `storage.py`; `bao.py` retains task-list updates and error messages.
- All **13 supplied tests passed unchanged**. Missing-file handling, error propagation, and standalone script error display were also verified.

## refactor step 5

Extract the repeated deadline date-and-time formatting from `handle_list()`, `handle_deadline()`, and `handle_due()` into `format_deadline(when: datetime) -> str` in `ui.py`.

Replace the three formatting blocks with calls to this function. This centralizes display formatting in `ui` and keeps deadline dates consistent.

Preserve the existing display format and verify it with the supplied tests.

### Step 5 results

- Extracted `format_deadline()` into `ui.py` and reused it in all three handlers, preserving the display format.
- All **13 supplied tests passed unchanged**. Standalone script formatting was also verified.

## refactor step 6

Extract repeated task formatting from `handle_list()` and the four add handlers into `format_task(task: dict[str, Any]) -> str` in `ui.py`. Reuse `format_deadline()` for deadline dates.

Replace the formatting blocks with calls to this function, centralizing how each task kind is displayed. Preserve existing numbering, indentation, messages, and notes.

Verify the changes with the supplied tests.

### Step 6 results

- Extracted `format_task()` into `ui.py`, reusing `format_deadline()`, and called it from `handle_list()` and all four add handlers.
- Existing display formatting is preserved. All **13 supplied tests passed unchanged**.

## refactor step 7

Extract the repeated added-task confirmation from the four add handlers into `show_added(task: dict[str, Any]) -> None` in `ui.py`.

Replace the two-line display blocks with calls to this function. This centralizes the confirmation message and indentation in `ui`, reusing `format_task()`.

Preserve existing output and verify it with the supplied tests.

### Step 7 results

- Extracted `show_added()` into `ui.py` and reused it in all four add handlers, preserving confirmation output.
- All **13 supplied tests passed unchanged**.
