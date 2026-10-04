# bao

## What is bao?

`bao` is a command-line task tracker built during the AIAP 23a software engineering bootcamp.
This repository contains two applications:

- `inherited/`: the original application used for the Day 2 refactoring exercise.
- `src/bao/`: the main application developed from the course stages.

## Setup

The project uses Python 3.13 and `uv`:

```bash
uv sync
uv run python --version
```

## Run and quality-check `inherited/bao`

Run the inherited application from the repository root:

```bash
uv run python inherited/bao.py
```

Run its tests:

```bash
uv run python -m pytest inherited/tests
```

Run its quality checks:

```bash
uv run ruff check .
uv run mypy .
uv run pytest
```

## Run and quality-check `src/bao`

Run the main application from the repository root:

```bash
uv run bao
```

Tasks are persisted in `data/tasks.json`. The file and its parent directory are created when
tasks are first saved.

Run the `src/bao` tests:

```bash
uv run pytest
```

Run the `src/bao` quality checks:

```bash
uv run ruff check .
uv run mypy .
uv run pytest
```

## Commands supported by `bao`

| Command | Purpose |
| --- | --- |
| `todo <description>` | Add a todo task. |
| `deadline <description> /by YYYY-MM-DD [HHMM]` | Add a task with a deadline. |
| `event <description> /from YYYY-MM-DD HHMM /to YYYY-MM-DD HHMM` | Add an event. |
| `recurring <description> /every <rule>` | Add a recurring task. |
| `list` | List all saved tasks. |
| `due YYYY-MM-DD [HHMM]` | Find deadlines due on a date or at a time. |
| `find <text>` | Search task descriptions. |
| `mark <number>` | Mark a task as done. |
| `unmark <number>` | Mark a task as incomplete. |
| `note <number> <note>` | Replace a task's note. |
| `delete <number>` | Delete a task. |
| `bye` | Exit the interactive session. |



## Example conversation

```text
$ uv run bao
Hello! I'm bao. What needs doing?
> todo buy groceries
Added:
[T][ ]buy groceries
> deadline submit report /by 2026-10-10 1700
Added:
[D][ ]submit report (by: Oct 10 2026, 5pm)
> list
1. [T][ ]buy groceries
2. [D][ ]submit report (by: Oct 10 2026, 5pm)
That's 2 on your plate.
> mark 1
Done:
[T][X]buy groceries
> note 2 include the monthly figures
Noted:
[D][ ]submit report (by: Oct 10 2026, 5pm)
Note: include the monthly figures
> find report
1. [D][ ]submit report (by: Oct 10 2026, 5pm)
> bye
Later.
```

### `src/bao/` file responsibilities

```text
src/bao/
├── __init__.py
│   └── Marks `bao` as a Python package.
├── cli.py
│   └── Starts the application, reads user input, and runs the command loop.
├── read_task_commands.py
│   └── Defines the command base class, command dispatcher, and read/control commands:
│       bye, list, due, and find.
├── add_task_commands.py
│   └── Defines commands that create tasks:
│       todo, deadline, event, and recurring.
├── modify_task_commands.py
│   └── Defines commands that modify tasks:
│       mark, unmark, note, and delete.
├── parser.py
│   └── Provides shared parsing helpers for dates, times, and task numbers.
├── task.py
│   └── Defines the different kinds of tasks and how they are displayed and saved.
└── tasks.py
    └── Manages the saved task list and JSON loading and saving.
```

## How to add a new command

Adding a command is intentionally simple, taking just 7 steps:

`src/bao/` is the easiest part of Bao to extend because each command's matching, parsing, and execution logic lives together in one command class.

### 1. Add a new command class

Create a subclass of `Command` in the appropriate module. For a command that creates a task, use
`src/bao/add_task_commands.py`. For a command that changes an existing task, use
`src/bao/modify_task_commands.py`.

For example:

```python
class CommandToDo(Command):
```

### 2. Add the command data in `__init__`

Store the command's keyword, usage text, regular-expression pattern, error message, and any values
the command will need later. `CommandToDo` receives the task description and keeps it in
`self.task_description`:

```python
def __init__(self, task_description: str) -> None:
    self.command_keyword = "todo"
    self.command_usage = "todo <description>"
    self.command_pattern = re.compile(r"^todo\s+(.+)$")
    self.unmatched_command_pattern_message = "Use: todo <description>"
    self.success_message_prefix = "Added:"
    self.task_description = task_description
```

### 3. Add `match_user_response_with_command_keyword`

This method does the quick routing check. It returns `True` for `todo` and `todo buy groceries`,
so the dispatcher knows this command may be responsible for the input:

```python
@classmethod
def match_user_response_with_command_keyword(cls, user_response: str) -> bool:
    command = cls("")
    return (
        user_response == command.command_keyword
        or user_response.startswith(f"{command.command_keyword} ")
    )
```

### 4. Add `parse_user_response_with_command_pattern`

This method validates the complete input. Use `fullmatch` so the whole response follows the
command's syntax. Return `None` when the keyword does not match, a usage message when the syntax
is invalid, or a fully initialized command when parsing succeeds:

```python
@classmethod
def parse_user_response_with_command_pattern(
    cls, user_response: str
) -> Command | str | None:
    if not cls.match_user_response_with_command_keyword(user_response):
        return None

    command = cls("")
    matched = command.command_pattern.fullmatch(user_response)
    if matched is None:
        return command.unmatched_command_pattern_message

    return cls(matched.group(1))
```

For `todo buy groceries`, `matched.group(1)` is `buy groceries`, so the returned command stores
that value in `self.task_description`.

### 5. Add `execute_command`

This method performs the command's action. `CommandToDo` creates a `TodoTask`, adds it to the task
collection, saves the collection, and returns the message displayed to the user:

```python
def execute_command(self, tasks: Tasks) -> str:
    task = TodoTask(self.task_description)
    tasks.append(task)
    tasks.save()
    return f"{self.success_message_prefix}\n{task}"
```

### 6. Register new command class in `COMMAND_CLASSES`:

Finally, register the new command class in the `COMMAND_CLASSES` tuple in `src/bao/read_task_commands.py`, alongside the existing command classes. The dispatcher loops through `COMMAND_CLASSES`, calls the keyword matcher, then calls the parser. Only the parsed command's `execute_command` method changes the task collection.

### 7. Run tests and quality checks

Add the new command's parsing and execution tests to `tests/test_bao.py`. Keep
`inherited/tests/` for tests of the separate inherited application.

Then run the tests and quality checks:

```bash
uv run pytest
uv run ruff check .
uv run mypy .
```
