# bao

## What is bao?

`bao` is a command-line task tracker chatbot application. It consists of two versions.

- `inherited/`: original application with non-modular code.
- `src/bao/`: main application with modular code.

## Documentation

- [Streamlit User Guide](STREAMLIT_USER_GUIDE.md)
- [Developer documentation](docs/)

## Setup

The project uses Python 3.13 and `uv`:

```bash
uv sync
uv run python --version
```

## Run the application

### Run `src/bao`

Run the main application from the repository root:

```bash
uv run bao
```

Tasks are persisted in `data/tasks.json`. The file and its parent directory are created when
tasks are first saved.

### Run `inherited/bao`

Run the inherited application from the repository root:

```bash
uv run python inherited/bao.py
```

## Contributor workflow

1. Create a branch in VS Code.
2. Make and test your changes.
3. Stage and commit the changes.
4. Push the branch.
5. Open a merge request in GitLab.
6. Review the merge request and approve it, if you are an approver.
7. Merge once the required checks and approvals pass.

## Continuous Integration (CI)

The GitLab CI pipeline configuration is:

```yaml
image: python:3.13-slim

stages:
  - checks

workflow:
  rules:
    - if: '$CI_PIPELINE_SOURCE == "push"'
    - if: '$CI_PIPELINE_SOURCE == "api"'

checks:
  stage: checks
  before_script:
    - pip install --no-cache-dir uv
    - uv sync --frozen
  script:
    - uv run ruff format --check .
    - uv run ruff check src tests
    - uv run mypy src tests
    - uv run pytest
```

### Trigger CI automatically on push

GitLab CI runs automatically when you push a commit or tag:

```bash
git push
```

### Trigger CI manually from VS Code

To trigger the pipeline manually from VS Code:

1. Install and authenticate the **GitLab for VS Code** extension.
2. Press `Cmd/Ctrl + Shift + P`.
3. Run **GitLab: Pipeline Actions - View, Create, Retry, or Cancel**.
4. Select **Create New Pipeline from Current Branch**.

The manual pipeline runs the project's configured format, lint, type-checking, and test checks.

## Commands supported by `bao`

| Command | Purpose |
| --- | --- |
| `todo <description> [/on YYYY-MM-DD]` | Add a dated todo task. |
| `deadline <description> /by YYYY-MM-DD [HHMM]` | Add a task with a deadline. |
| `event <description> /from YYYY-MM-DD HHMM /to YYYY-MM-DD HHMM` | Add an event. |
| `recurring <description> /every <rule>` | Add a recurring task, such as `Wednesday at 21:00`. |
| `list` | List all saved tasks. |
| `due YYYY-MM-DD [HHMM]` | Find deadlines due on a date or at a time. |
| `find <text>` | Search task descriptions. |
| `filter <type>` | List tasks of one type: `todo`, `deadline`, `event`, or `recurring`. |
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
> filter todo
1. [T][ ]buy groceries
> bye
Later.
```

## Architecture

### `src/bao/` file responsibilities

```text
src/bao/
├── __init__.py
│   └── Marks `bao` as a Python package.
├── cli.py
│   └── Starts the application, reads user input, and runs the command loop.
├── read_task_commands.py
│   └── Defines the command base class, command dispatcher, and read/control commands:
│       bye, list, due, find, and filter.
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

Create a subclass of `Command` in the appropriate module. For a command that reads tasks, use
`src/bao/read_task_commands.py`. For a command that creates a task, use
`src/bao/add_task_commands.py`. For a command that changes an existing task, use
`src/bao/modify_task_commands.py`.

For example, add `CommandFilter` to `src/bao/read_task_commands.py`:

```python
class CommandFilter(Command):
```

### 2. Add the command data in `__init__`

Store the command's keyword, usage text, regular-expression pattern, error message, and task type
in `self.task_type`:

```python
def __init__(self, task_type: str) -> None:
    self.command_keyword = "filter"
    self.command_usage = "filter <type>"
    self.command_pattern = re.compile(r"^filter\s+(.+)$")
    self.unmatched_command_pattern_message = "Use: filter <type>"
    self.no_matching_tasks_message = f'No tasks found of type "{task_type}".'
    self.task_type = task_type
```

### 3. Add `match_user_response_with_command_keyword`

This method does the quick routing check. It returns `True` for `filter` and `filter todo`,
so the dispatcher knows this command may be responsible for the input:

```python
@classmethod
def match_user_response_with_command_keyword(cls, user_response: str) -> bool:
    command = cls("todo")
    return user_response == command.command_keyword or user_response.startswith(
        f"{command.command_keyword} "
    )
```

### 4. Add `parse_user_response_with_command_pattern`

This method validates the complete input and accepts only the supported task types. Use `fullmatch`
so the whole response follows the command's syntax. Return `None` when the keyword does not match,
a usage message when the syntax or type is invalid, or a fully initialized command when parsing
succeeds:

```python
@classmethod
def parse_user_response_with_command_pattern(
    cls, user_response: str
) -> Command | str | None:
    if not cls.match_user_response_with_command_keyword(user_response):
        return None

    command = cls("todo")
    matched = command.command_pattern.fullmatch(user_response)
    if matched is None or matched.group(1) not in TASK_TYPES:
        return command.unmatched_command_pattern_message

    return cls(matched.group(1))
```

For `filter todo`, `matched.group(1)` is `todo`, so the returned command stores that value in
`self.task_type`.

### 5. Add `execute_command`

This method selects tasks whose `task_type` matches the requested type, numbers them for display,
and returns a no-match message when appropriate. A read-only command does not call `tasks.save()`:

```python
def execute_command(self, tasks: Tasks) -> str:
    matches = [task for task in tasks if task.task_type == self.task_type]
    if not matches:
        return self.no_matching_tasks_message

    numbered_tasks = _number_tasks_for_display(matches)
    return "\n".join(numbered_tasks)
```

### 6. Register new command class in `COMMAND_CLASSES`

Finally, register `CommandFilter` in the `COMMAND_CLASSES` tuple in
`src/bao/read_task_commands.py`, alongside the existing command classes. The dispatcher loops
through `COMMAND_CLASSES`, calls the keyword matcher, then calls the parser. Only the parsed
command's `execute_command` method reads the task collection; it does not change it.

### 7. Trigger CI and complete the merge request

Add tests for each supported task type, a valid type with no matching tasks, and invalid filter
input to `tests/test_bao.py`. Keep `inherited/tests/` for tests of the separate inherited
application.

Then trigger GitLab CI from VS Code using instructions in [Trigger CI manually from VS Code](#trigger-ci-manually-from-vs-code).
