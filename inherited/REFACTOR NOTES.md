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

## refactor step 8

Reuse `format_task()` in `handle_due()` to replace its separate deadline formatting and completion-box logic. Keep numbering in the handler and preserve existing output.

This centralizes due-task display formatting in `ui.py`. Verify the change with the supplied tests.

### Step 8 results

- `handle_due()` now uses `format_task()`, preserving numbering and output. Removed the unused `format_deadline` imports from the handlers module.
- All **13 supplied tests passed unchanged**.


## refactor step 9

Extract three UI responsibilities into `ui.py`:

- `format_task_summary(task: dict[str, Any]) -> str`: share completion-box and description formatting between `handle_mark_unmark()` and `handle_find()`, keeping indentation and numbering in the handlers.
- `show_tasks(tasks: list[dict[str, Any]]) -> None`: move the empty-list message, numbered task display, and optional notes from `handle_list()` into UI, reusing `format_task()`.
- `show_tasks_left(count: int) -> None`: share the remaining-task message between `handle_delete()` and `handle_clear()`.

Preserve existing output and verify the changes with the supplied tests without modifying them.

### Step 9 results

- Added `format_task_summary()`, `show_tasks()`, and `show_tasks_left()` to `ui.py` and reused them in the relevant handlers, preserving existing output.
- All **13 supplied tests passed unchanged**.

## refactor step 10

Extract three confirmation-message blocks into `ui.py`:

- `show_marked(task: dict[str, Any]) -> None`: move the completion-state heading and indented summary from `handle_mark_unmark()`, choosing the heading from `task["done"]` and reusing `format_task_summary()`.
- `show_noted(task: dict[str, Any]) -> None`: move the note confirmation from `handle_note()`, using the updated task's description and note.
- `show_deleted(task: dict[str, Any], remaining_count: int) -> None`: move the deletion confirmation from `handle_delete()`, reusing `show_tasks_left()`.

Preserve existing output and verify the changes with the supplied tests without modifying them.

### Step 10 results

- Added `show_marked()`, `show_noted()`, and `show_deleted()` to `ui.py` and called them from the corresponding handlers, preserving confirmation output.
- All **13 supplied tests passed unchanged**.

## refactor step 11

Extract three input-parsing helpers into a new `parser.py`:

- `parse_task_index(text: str) -> int`: share integer conversion and subtraction between mark/unmark, note, and delete. Keep task-existence checks in the handlers as a tasklist responsibility.
- `parse_required_pair(text: str, separator: str, error_message: str) -> tuple[str, str]`: share separator checks, splitting once, whitespace stripping, and required-value checks between deadline and recurring commands.
- `parse_deadline_datetime(text: str) -> datetime`: move the deadline date-format loop into parser, accepting a date with an optional four-digit time.

Helpers return parsed values or raise `ValueError` with the existing input-error messages. Handlers display those errors and return. Preserve existing behavior and run the supplied tests without modifying them.

### Step 11 results

- Added all three helpers to `parser.py` and reused them in the relevant handlers, preserving input errors and leaving task-existence checks in place.
- All **13 supplied tests passed unchanged**. Standalone script imports and parser error output were also verified.

## refactor step 12

Extract three parsing blocks into `parser.py`:

- `parse_event(line: str) -> tuple[str, str, str]`: move event separator checks, splitting, whitespace stripping, and required-value validation out of `handle_event()`, returning description, start, and end.
- `parse_note(line: str) -> tuple[int, str]`: move note argument validation and task-number parsing out of `handle_note()`, reusing `parse_task_index()` and preserving note whitespace with `split(maxsplit=2)`.
- `parse_due_date(text: str) -> date`: move due-date conversion out of `handle_due()`, preserving the existing input-error message and leaving deadline selection in the handler.

Helpers return parsed values or raise `ValueError`. Handlers display expected input errors. Preserve existing behavior, including the uncaught event error for incorrectly ordered separators and the original number text in missing-task errors. Run the supplied tests without modifying them.

### Step 12 results

- Added `parse_event()`, `parse_note()`, and `parse_due_date()` and reused them in the corresponding handlers, preserving existing behavior.
- All **13 supplied tests passed unchanged**. Compared 13 representative cases against the previous handlers, including note whitespace, original number text, and malformed event separators; standalone imports also verified.

## refactor step 13

Extract three parser helpers into `parser.py`:

- `parse_task_number_command(line: str, error_message: str) -> int`: share command splitting, argument-count validation, and `parse_task_index()` between mark/unmark and delete. Preserve their usage messages and keep task-existence checks outside parser.
- `parse_required_text(text: str, error_message: str) -> str`: share whitespace stripping and empty-argument validation between to-do and find, preserving their different error messages.
- `parse_deadline(line: str) -> tuple[str, datetime]`: combine deadline-prefix removal, `parse_required_pair()`, and `parse_deadline_datetime()` into one parser entry point returning description and deadline.

Preserve existing behavior and run the supplied tests without modifying them.

### Step 13 results

- Added `parse_task_number_command()`, `parse_required_text()`, and `parse_deadline()` and reused them in the relevant handlers, preserving existing behavior.
- All **13 supplied tests passed unchanged**. Compared 25 representative cases against the previous handlers; standalone execution also verified.

## refactor step 14

Extract three command wrappers into `parser.py`:

- `parse_recurring(line: str) -> tuple[str, str]`: move prefix removal and the `parse_required_pair()` call from `handle_recurring()` into parser, returning description and interval with the existing usage message.
- `parse_todo(line: str) -> str`: move prefix removal and the to-do error message into parser, reusing `parse_required_text()` to return a validated description.
- `parse_find(line: str) -> str`: move prefix removal and the find error message into parser, reusing `parse_required_text()` to return a validated search query.

These wrappers complete responsibility separation rather than remove further duplication. Preserve existing behavior and run the supplied tests without modifying them.

### Step 14 results

- Added `parse_recurring()`, `parse_todo()`, and `parse_find()` and called them from the corresponding handlers, preserving parsing behavior and error messages.
- All **13 supplied tests passed unchanged**.

## refactor step 15

Extract three command-specific parsing helpers into `parser.py`:

- `parse_due(line: str) -> date`: move due-prefix removal and whitespace stripping into parser, reusing `parse_due_date()`.
- `parse_delete(line: str) -> int`: wrap `parse_task_number_command()` with delete's existing usage message.
- `parse_mark_unmark(line: str) -> tuple[str, int]`: move command-name extraction and usage-message construction into parser, reusing `parse_task_number_command()` and returning the command and task index.

Preserve existing behavior and run the supplied tests without modifying them.

### Step 15 results

- Added `parse_due()`, `parse_delete()`, and `parse_mark_unmark()` and called them from the corresponding handlers, preserving parsing behavior and error messages.
- All **13 supplied tests passed unchanged**.

## refactor step 16

Extract three task-list operations into a new `tasklist.py`:

- `validate_task_index(tasks: list[dict[str, Any]], index: int) -> None`: share bounds checking between mark/unmark, note, and delete, raising `IndexError` for an invalid index. Handlers retain the existing missing-task message and original number text.
- `clear_completed(tasks: list[dict[str, Any]]) -> int`: remove completed tasks in place and return the number removed, leaving display and saving in the handler.
- `find_tasks(tasks: list[dict[str, Any]], query: str) -> list[dict[str, Any]]`: return case-insensitive description matches in their existing order, leaving display in the handler.

Preserve existing behavior and run the supplied tests without modifying them.

### Step 16 results

- Added `validate_task_index()`, `clear_completed()`, and `find_tasks()` to `tasklist.py` and reused them in the relevant handlers, preserving existing behavior.
- All **13 supplied tests passed unchanged**. Standalone task-list operations and exact output were also verified.

## refactor step 17

Extract three more operations into `tasklist.py`:

- `due_tasks(tasks: list[dict[str, Any]], wanted: date) -> list[dict[str, Any]]`: move deadline filtering and stored-date conversion out of `handle_due()`, returning matches in their existing order.
- `set_done(tasks: list[dict[str, Any]], index: int, done: bool) -> None`: validate the index with `validate_task_index()` and update completion state in place.
- `set_note(tasks: list[dict[str, Any]], index: int, note: str) -> None`: validate the index with the same helper and replace the note in place.

Handlers retain missing-task errors, confirmation display, and saving. Preserve existing behavior and run the supplied tests without modifying them.

### Step 17 results

- Added `due_tasks()`, `set_done()`, and `set_note()` and called them from the corresponding handlers, preserving selection order, mutations, and existing messages. Stored-date conversion now lives in tasklist.
- All **13 supplied tests passed unchanged**.

## refactor step 18

Extract three operations into `tasklist.py`:

- `delete_task(tasks: list[dict[str, Any]], index: int) -> dict[str, Any]`: combine index validation and removal, returning the removed task for confirmation.
- `add_todo(tasks: list[dict[str, Any]], description: str) -> dict[str, Any]`: construct and append a to-do task with the existing defaults, returning the new task for display.
- `add_deadline(tasks: list[dict[str, Any]], description: str, when: datetime) -> dict[str, Any]`: construct and append a deadline task, including ISO date conversion and existing defaults, returning the new task for display.

Handlers retain error messages, confirmation display, and saving. Preserve existing behavior and run the supplied tests without modifying them.

### Step 18 results

- Added `delete_task()`, `add_todo()`, and `add_deadline()` and called them from the corresponding handlers, preserving task defaults, stored dates, and existing behavior.
- All **13 supplied tests passed unchanged**.

## refactor step 19

Centralize expected input-error handling across parser, UI, and coordination:

- Define `InputError(ValueError)` in `parser.py` and raise it for deliberate input-validation failures, distinguishing these from unexpected exceptions without comparing error-message text.
- Add `show_error(message: str) -> None` to `ui.py` to own error display.
- Catch `InputError` once around command routing in `run()`, display it through `show_error()`, and continue the input loop. Remove the repeated parsing catches from handlers, allowing expected input errors to propagate to the coordinator.

Keep tasklist `IndexError` handling separate and preserve unexpected exceptions, including the existing event unpacking error. Preserve conversation output and save behavior, and run the supplied tests without modifying them.

### Step 19 results

- Added `InputError` and `show_error()`, centralized the catch in `run()`, and removed nine handler parsing catches plus the event message comparison. Tasklist error handling remains separate.
- All **13 supplied tests passed unchanged**. Standalone checks verified 15 expected error cases, continued processing and saved state, and propagation of the unexpected event error.

## refactor step 20

Move three display blocks into `ui.py`: `show_due_tasks(tasks)` for numbered deadlines or the empty-result message, `show_found_tasks(tasks)` for numbered search summaries or the empty-result message, and `show_cleared(removed_count, remaining_count)` for clear confirmation. Reuse existing formatters and `show_tasks_left()`; preserve output and run the supplied tests unchanged.

### Step 20 results

- Added all three UI helpers and replaced the corresponding handler display blocks, preserving output.
- All **13 supplied tests passed unchanged**.

## refactor step 21

Define `TaskNotFoundError(IndexError)` in `tasklist.py` and raise it for invalid task indexes. Catch it once in `run()`, preserving the original task-number text and displaying the existing message through `show_error()`. Remove the three handler catches; keep unrelated `IndexError`s propagating and run the supplied tests unchanged.

### Step 21 results

- Added `TaskNotFoundError`, centralized its catch in `run()`, and removed three handler catches.
- All **13 supplied tests passed unchanged**. Verified original number text, continued processing, no save on failure, and propagation of unrelated `IndexError`s.

## refactor step 22

Introduce a shared `Task` dataclass and `TodoTask`, `DeadlineTask`, `EventTask`, and `RecurringTask` subclasses in `tasks.py`. Centralize shared defaults and kind-specific fields; use `to_dict()` to preserve existing JSON keys, key order, and date format. Route all four task-creation operations through tasklist. This first migration stage keeps dictionary-based callers; using objects throughout and converting at the storage boundary remains a later stage. Run the supplied tests unchanged.

### Step 22 results

- Added all five task dataclasses and shared dictionary conversion; all four add operations now construct tasks through the models. Existing callers still use dictionaries.
- All **13 supplied tests passed unchanged**. Verified model conversion, exact saved JSON for every task kind, and standalone execution.
