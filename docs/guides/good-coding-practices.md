# Good Coding Practices

## How to Name Internal Methods and Static Methods

In `src/bao/tasks.py`, `_append_task` is an internal method, so it uses a single leading underscore. It uses the instance's task list and saves through the storage layer:

```python
class Tasks:
    def _append_task(self, task: Task) -> None:
        """
        Appends a task and persists the changed task list.

        Args:
        -----
        task (Task): The task to append and save.

        Returns:
        --------
        None.
        """
        self.tasks.append(task)
        self._save_tasks()
```

The current codebase does not need a static method for this operation because `_append_task` works with instance state. Add `@staticmethod` only when a helper genuinely does not need instance or class state.

## When to Use OOP vs Functions

In `src/bao/task.py`, `Task` is an object because each instance represents one task, owns task-specific state, and provides behavior that changes that state:

```python
class Task:
    """Shared state and behavior for every task type."""

    # Identity: each Task instance represents one distinct task object.
    task_type = ""

    def __init__(
        self,
        description: str,
        task_type: str | None = None,
        *,
        done: bool = False,
        note: str | None = None,
    ) -> None:
        # State: these attributes describe the task's current condition.
        self.description = description
        self.done = done
        self.note = note
        if task_type is not None:
            self.task_type = task_type

    # Behavior: this method changes the task's completion state.
    def mark_done(self) -> None:
        """
        Marks this task as complete by setting its done status to True.

        Returns:
        --------
        None.
        """
        self.done = True

    def unmark_done(self) -> None:
        """
        Marks this task as incomplete by setting its done status to False.

        Returns:
        --------
        None.
        """
        self.done = False
```

`description`, `done`, and `note` are state. `mark_done()`, `unmark_done()`, and `add_note()` are behavior. Identity comes from each distinct `Task` instance, rather than from an invented `task_id` field.

Use a function when the operation is a focused transformation or validation and does not need to own changing state. `src/bao/parser.py` uses `_parse_find` this way:

```python
def _parse_find(match: re.Match[str]) -> Command | ParseError:
    """
    Builds a parsed find command or its usage error.

    Args:
    -----
    match (re.Match[str]): The regular-expression match containing the query.

    Returns:
    --------
    Command | ParseError: The parsed command or its usage error.
    """
    query = match.group(1)
    if re.fullmatch(r"\S(?:.*\S)?\s*", query) is None:
        return ParseError("Use: find <text>")
    return Command("find", query=query.strip())
```

A separate class for `_parse_find` would add structure without clarifying ownership or state.

## Good Docstring and Type Hint Examples

Use the project’s NumPy-style docstrings and explicit type hints. Describe
arguments and return values when they are present:

```python
def to_dict(self) -> dict[str, Any]:
    """
    Converts this task's shared fields to a JSON-ready dictionary.

    Returns:
    --------
    dict[str, Any]: The shared task fields and its type marker.
    """
    return {
        "description": self.description,
        "done": self.done,
        "note": self.note,
        "type": self.task_type,
    }
```

For functions that accept arguments and return values, document both using
the same style:

```python
def _parse_find(match: re.Match[str]) -> Command | ParseError:
    """
    Builds a parsed find command or its usage error.

    Args:
    -----
    match (re.Match[str]): The regular-expression match containing the query.

    Returns:
    --------
    Command | ParseError: The parsed command or its usage error.
    """
    query = match.group(1)
    if re.fullmatch(r"\S(?:.*\S)?\s*", query) is None:
        return ParseError("Use: find <text>")
    return Command("find", query=query.strip())
```
