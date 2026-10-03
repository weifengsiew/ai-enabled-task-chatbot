"""Define the Tasks class for managing and persisting task objects."""

from collections.abc import Iterator

from .storage import load_tasks, save_tasks
from .task import Task


class Tasks:
    """Owns the mixed task list and its state-changing operations."""

    def __init__(self) -> None:
        """Load the saved mixed task list."""
        # State
        self._items: list[Task] = load_tasks()

    def save(self) -> None:
        """Persist the current task list."""
        save_tasks(self._items)

    def append(self, task: Task) -> None:
        """Append a task to the task list."""
        self._items.append(task)

    def __iter__(self) -> Iterator[Task]:
        """Iterate over the tasks in the task list."""
        return iter(self._items)

    def __len__(self) -> int:
        """Return the number of tasks in the task list."""
        return len(self._items)

    def __getitem__(self, index: int) -> Task:
        """Return the task at the requested zero-based index."""
        return self._items[index]

    def pop(self, index: int) -> Task:
        """Remove and return the task at the requested zero-based index."""
        return self._items.pop(index)
