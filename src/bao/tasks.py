"""Task collection and persistence for Bao."""

from collections.abc import Iterator

from .storage import load_tasks, save_tasks
from .task import Task


class Tasks:
    """Owns the mixed task list and its state-changing operations."""

    def __init__(self) -> None:
        """Loads the saved mixed task list."""
        self._items: list[Task] = load_tasks()

    def save(self) -> None:
        """Persists the current task list."""
        save_tasks(self._items)

    def append(self, task: Task) -> None:
        """Appends a task to the collection."""
        self._items.append(task)

    def __iter__(self) -> Iterator[Task]:
        """Iterates over the tasks in the collection."""
        return iter(self._items)

    def __len__(self) -> int:
        """Returns the number of tasks in the collection."""
        return len(self._items)

    def __getitem__(self, index: int) -> Task:
        """Returns the task at the requested zero-based index."""
        return self._items[index]

    def pop(self, index: int) -> Task:
        """Removes and returns the task at the requested zero-based index."""
        return self._items.pop(index)
