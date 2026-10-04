"""Task-list operations for the inherited Bao application."""

from collections.abc import Iterator
from datetime import date, datetime
from typing import Any

if __package__:
    from .task import DeadlineTask, EventTask, RecurringTask, TodoTask
else:
    from task import DeadlineTask, EventTask, RecurringTask, TodoTask


class TaskNotFoundError(IndexError):
    """The requested task index is outside the current task list."""


class Tasks:
    """Own an ordered collection of task dictionaries and its operations."""

    def __init__(self, items: list[dict[str, Any]]) -> None:
        """Initialize the collection from a shallow copy of the supplied list.

        Args:
            items: Initial task dictionaries, retained by reference.

        Returns:
            None.
        """
        self._items = list(items)

    def __iter__(self) -> Iterator[dict[str, Any]]:
        """Return an iterator over task references in collection order.

        Returns:
            An iterator over the stored task dictionaries.
        """
        return iter(self._items)

    def __len__(self) -> int:
        """Return the number of tasks without modifying the collection.

        Returns:
            The current task count.
        """
        return len(self._items)

    def __getitem__(self, index: int) -> dict[str, Any]:
        """Return a task reference using normal list-indexing semantics.

        Args:
            index: Task index; negative indexes count from the end.

        Returns:
            The stored task dictionary at the requested index.

        Raises:
            IndexError: If the index is outside the collection.
        """
        return self._items[index]

    def clear(self) -> None:
        """Remove all tasks from this collection in place.

        Returns:
            None.
        """
        self._items.clear()

    def extend(self, items: list[dict[str, Any]]) -> None:
        """Append supplied task references to the collection in order.

        Args:
            items: Task dictionaries to append, such as data loaded by storage.

        Returns:
            None.
        """
        self._items.extend(items)

    def to_list(self) -> list[dict[str, Any]]:
        """Return a shallow list copy suitable for the existing storage format.

        Returns:
            A new list containing the stored dictionary references in order.
            Editing those dictionaries also changes the collection's tasks.
        """
        return list(self._items)

    def _validate_index(self, index: int) -> None:
        """Check that an index identifies a task without changing the list.

        Args:
            index: Zero-based task index to validate.

        Returns:
            None.

        Raises:
            TaskNotFoundError: If the index is negative or outside the collection.
        """
        if index < 0 or index >= len(self._items):
            raise TaskNotFoundError(index)

    def clear_completed(self) -> int:
        """Remove completed tasks in place and count the removals.

        Returns:
            The number of completed tasks removed.
        """
        before = len(self._items)
        self._items[:] = [task for task in self._items if not task["done"]]
        return before - len(self._items)

    def find(self, query: str) -> list[dict[str, Any]]:
        """Find tasks whose descriptions contain a query, ignoring case.

        Args:
            query: Substring to match against task descriptions.

        Returns:
            A new list of matching task references in their original order.
        """
        return [
            task
            for task in self._items
            if query.casefold() in task["description"].casefold()
        ]

    def due(self, wanted: date) -> list[dict[str, Any]]:
        """Select deadline tasks due on a calendar date without changing the list.

        Args:
            wanted: Calendar date to match against stored deadline dates.

        Returns:
            A new list of matching task references in their original order.
        """
        return [
            task
            for task in self._items
            if task["kind"] == "deadline"
            and datetime.fromisoformat(task["when"]).date() == wanted
        ]

    def set_done(self, index: int, done: bool) -> None:
        """Validate a task index and update its completion state in place.

        Args:
            index: Zero-based task index.
            done: Completion state to assign.

        Returns:
            None.

        Raises:
            TaskNotFoundError: If the index is negative or outside the collection.
        """
        self._validate_index(index)
        self._items[index]["done"] = done

    def set_note(self, index: int, note: str) -> None:
        """Validate a task index and replace its note in place.

        Args:
            index: Zero-based task index.
            note: Note text to assign without changing its whitespace.

        Returns:
            None.

        Raises:
            TaskNotFoundError: If the index is negative or outside the collection.
        """
        self._validate_index(index)
        self._items[index]["note"] = note

    def delete(self, index: int) -> dict[str, Any]:
        """Validate an index and remove its task from the list in place.

        Args:
            index: Zero-based index of the task to remove.

        Returns:
            The removed task for confirmation display.

        Raises:
            TaskNotFoundError: If the index is negative or outside the collection.
        """
        self._validate_index(index)
        return self._items.pop(index)

    def add_todo(self, description: str) -> dict[str, Any]:
        """Construct a to-do task and append it to the collection in place.

        Args:
            description: Parsed task description.

        Returns:
            The appended task, initially incomplete with an empty note.
        """
        task = TodoTask(description=description).to_dict()
        self._items.append(task)
        return task

    def add_deadline(self, description: str, when: datetime) -> dict[str, Any]:
        """Construct a deadline task and append it to the collection in place.

        Args:
            description: Parsed task description.
            when: Parsed deadline datetime to store in ISO format.

        Returns:
            The appended task, initially incomplete with an empty note.
        """
        task = DeadlineTask(description=description, when=when).to_dict()
        self._items.append(task)
        return task

    def add_event(self, description: str, start: str, end: str) -> dict[str, Any]:
        """Construct an event task and append its dictionary to the list in place.

        Args:
            description: Parsed task description.
            start: Parsed event start text.
            end: Parsed event end text.

        Returns:
            The appended task, initially incomplete with an empty note.
        """
        task = EventTask(description=description, start=start, end=end).to_dict()
        self._items.append(task)
        return task

    def add_recurring(self, description: str, every: str) -> dict[str, Any]:
        """Construct a recurring task and append its dictionary to the list in place.

        Args:
            description: Parsed task description.
            every: Parsed recurrence interval text.

        Returns:
            The appended task, initially incomplete with an empty note.
        """
        task = RecurringTask(description=description, every=every).to_dict()
        self._items.append(task)
        return task
