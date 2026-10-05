# AI-Enabled Task Chatbot

An AI-enabled conversational task manager for capturing, organizing, and retrieving everyday tasks, including to-dos, 
deadlines, events, and recurring tasks. It combines explicit task commands with a natural-language interface powered 
by an LLM, so users can manage tasks without navigating complex command syntax.

## Video Demo

Watch the AI-Enabled Task Chatbot demo on YouTube:

[![Watch the AI-Enabled Task Chatbot demo](https://img.youtube.com/vi/Bg8MmsV6iBM/hqdefault.jpg)](https://youtu.be/Bg8MmsV6iBM?is=1H__O-CL5IOFH3Sn)

## User Guide

- [Streamlit User Guide](STREAMLIT_USER_GUIDE.md)
- [Cat theme specification](docs/specifications/cat-theme-spec.md)
- [Developer documentation](docs/)

## Cat-themed Streamlit UI

Bao’s Streamlit workspace uses a local cat illustration for each major
workflow and task type, making the visual language easy to recognize.

| Chat | Create task | Search and update |
| --- | --- | --- |
| ![Bao chat cat](assets/cats/chat-cat.png) | ![Bao painting cat](assets/cats/create-cat.png) | ![Bao detective cat](assets/cats/search-cat.png) |

| Todo | Deadline | Recurring | Event |
| --- | --- | --- | --- |
| ![Bao homework cat](assets/cats/todo-cat.png) | ![Bao clock cat](assets/cats/deadline-cat.png) | ![Bao yarn-ball cat](assets/cats/recurring-cat.png) | ![Bao event cat](assets/cats/event-cat.png) |

## Setup and run `bao`

Requires Python 3.13 and uv. From the repository root, install dependencies and start the CLI:

```bash
uv sync
uv run python --version
uv run bao
```

To start the Streamlit app instead, run:

```bash
uv run streamlit run src/bao/streamlit_app.py \
  --server.address 127.0.0.1 \
  --server.port 7860
```

Then open [http://127.0.0.1:7860](http://127.0.0.1:7860) in your browser.

To enable AI assistance, configure the OpenAI-compatible LLM endpoint, model, and API key, then enable **Ask Bao AI** in Streamlit. See the [LLM setup instructions](STREAMLIT_USER_GUIDE.md#configure-the-api-key-and-start-bao-with-llm-assistance).

## Project Motivation

This project explores how LLM-powered conversational interfaces can make everyday task management feel more natural, while Python keeps tasks structured and the codebase testable and easy to extend.

## Chatbot Feature Highlights

- Manage tasks conversationally through a Command Line Interface (CLI) or Streamlit App Interface.
- Create, search, update, filter, and view tasks using easy-to-use buttons.

## Best Practices Highlights

- Object-oriented programming: Shared `Task` and `Command` base classes with subclasses for specific task and command types.
- Modular architecture:
  - Interface modules: `cli.py` and `streamlit_app.py` handle user interaction.
  - Command modules: `read_task_commands.py`, `add_task_commands.py`, and `modify_task_commands.py` handle task queries, creation, and updates.
  - Supporting modules: `parser.py` parses dates, times, and task numbers; `task.py` defines task types and their display and serialization; `tasks.py` manages the task list and JSON loading and saving.
- Automated quality checks: GitHub Actions runs tests, ruff linting and formatting, and mypy type hint checking.
- Reproducible dependencies: `uv.lock` records dependency versions for consistent installs.

## Python Frameworks

<p align="center">
  <img alt="Python 3.13" src="https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img alt="Streamlit" src="https://img.shields.io/badge/Streamlit-Application%20Interface-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white">
  <img alt="OpenAI" src="https://img.shields.io/badge/OpenAI-LLM%20Integration-412991?style=for-the-badge&logo=openai&logoColor=white">
  <img alt="uv" src="https://img.shields.io/badge/uv-Dependency%20Management-DE5FE9?style=for-the-badge">
  <img alt="pytest" src="https://img.shields.io/badge/pytest-Testing-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white">
  <img alt="Ruff" src="https://img.shields.io/badge/Ruff-Linting%20and%20Formatting-D7FF64?style=for-the-badge">
  <img alt="mypy" src="https://img.shields.io/badge/mypy-Type%20Checking-1674B8?style=for-the-badge">
  <img alt="GitHub Actions" src="https://img.shields.io/badge/GitHub%20Actions-CI-2088FF?style=for-the-badge&logo=githubactions&logoColor=white">
</p>

| Area | Python framework or tool |
| --- | --- |
| Application runtime | Python 3.13 |
| Command-line interface | Python standard library |
| Web application interface | Streamlit |
| LLM integration | OpenAI Python SDK, using an OpenAI-compatible endpoint |
| Dependency and environment management | uv |
| Automated testing | pytest |
| Linting and formatting | Ruff |
| Type checking | mypy |
| Continuous integration | GitHub Actions |

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

## Contributor workflow

1. Fork the repository on GitHub.
2. Clone your fork and open it in VS Code.
3. Create a branch for your changes.
4. Make your changes and run the project’s quality checks.
5. Commit and push your changes to your fork.
6. Open a pull request against the original repository.
7. Address review feedback and ensure required checks pass.
8. A maintainer merges the pull request after required approvals.

## Continuous Integration (CI) pipeline

GitHub Actions runs the project's formatting, linting, type-checking, and test checks on pushes
and pull requests.

To run the same checks locally:

```bash
uv sync --frozen
uv run ruff format --check .
uv run ruff check src tests
uv run mypy src tests
uv run pytest
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
│   └── Defines commands that modify existing tasks:
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

### 7. Trigger CI and complete the pull request

Add tests for each supported task type, a valid type with no matching tasks, and invalid filter
input to `tests/test_bao.py`.

Then open a pull request on GitHub and wait for the GitHub Actions checks to pass.
