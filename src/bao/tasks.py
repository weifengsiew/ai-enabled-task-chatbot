"""Task-list operations for Bao."""

from datetime import date, time

from .storage import load_tasks, save_tasks
from .task import DeadlineTask, EventTask, RecurringTask, Task, TodoTask


class Tasks:
    """Owns the mixed task list and its state-changing operations."""

    def __init__(self) -> None:
        """Loads the saved mixed task list."""
        self.tasks: list[Task] = load_tasks()

    def add_todo(self, description: str) -> TodoTask:
        """Adds and saves a to-do task."""
        task = TodoTask(description)
        self._append_task(task)
        return task

    def add_deadline(
        self, description: str, due_date: date, due_time: time | None
    ) -> DeadlineTask:
        """Adds and saves a deadline task."""
        task = DeadlineTask(description, due_date, due_time)
        self._append_task(task)
        return task

    def add_event(self, description: str, start: str, end: str) -> EventTask:
        """Adds and saves an event task."""
        task = EventTask(description, start, end)
        self._append_task(task)
        return task

    def add_recurring(self, description: str, day: str) -> RecurringTask:
        """Adds and saves a recurring task."""
        task = RecurringTask(description, day)
        self._append_task(task)
        return task

    def all_tasks(self) -> list[Task]:
        """Returns the tasks in their current order."""
        return self.tasks

    def incomplete_count(self) -> int:
        """Returns the number of incomplete tasks."""
        return sum(1 for task in self.tasks if not task.done)

    def due_tasks(self, query_date: date) -> list[Task]:
        """Returns deadline tasks due on the requested date."""
        return [
            task for task in self.tasks if getattr(task, "due_date", None) == query_date
        ]

    def find_tasks(self, query: str) -> list[Task]:
        """Returns tasks with the query in their descriptions."""
        search_text = query.casefold()
        return [
            task for task in self.tasks if search_text in task.description.casefold()
        ]

    def task_at(self, task_number: int) -> Task | None:
        """Returns a task by its one-based display number, if it exists."""
        if 1 <= task_number <= len(self.tasks):
            return self.tasks[task_number - 1]
        return None

    def mark(self, task_number: int) -> Task | None:
        """Marks a task done and saves the changed list."""
        task = self.task_at(task_number)
        if task is None:
            return None
        task.mark_done()
        self._save_tasks()
        return task

    def unmark(self, task_number: int) -> Task | None:
        """Marks a task incomplete and saves the changed list."""
        task = self.task_at(task_number)
        if task is None:
            return None
        task.unmark_done()
        self._save_tasks()
        return task

    def add_note(self, task_number: int, note: str) -> Task | None:
        """Replaces a task note and saves the changed list."""
        task = self.task_at(task_number)
        if task is None:
            return None
        task.add_note(note)
        self._save_tasks()
        return task

    def delete(self, task_number: int) -> tuple[Task, int] | None:
        """Removes a task and saves the changed list."""
        task = self.task_at(task_number)
        if task is None:
            return None
        self.tasks.pop(task_number - 1)
        self._save_tasks()
        return task, len(self.tasks)

    def _append_task(self, task: Task) -> None:
        """Appends a task and saves the changed list."""
        self.tasks.append(task)
        self._save_tasks()

    def _save_tasks(self) -> None:
        """Saves the current task list through the storage layer."""
        save_tasks(self.tasks)
