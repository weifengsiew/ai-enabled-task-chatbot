"""Define the parent Task class and child classes TodoTask, DeadlineTask,
EventTask, and RecurringTask.
"""

from datetime import date, datetime, time
from typing import Any


class Task:
    """Shared state and behavior for every task type."""

    # Identity: identifies the kind of task.
    task_type = ""

    def __init__(
        self,
        description: str,
        task_type: str | None = None,
        done: bool = False,
        note: str | None = None,
        task_id: int | None = None,
    ) -> None:
        """
        Initialize a task with its shared fields.

        Args:
        -----
        description (str): What needs to be done.
        task_type (str | None): An optional type marker for a generic task.
        done (bool): Whether the task is complete.
        note (str | None): An optional note attached to the task.
        task_id (int | None): The persisted ID shared across task types.

        Returns:
        --------
        None.
        """
        # State: these attributes describe the task's current condition.
        self.description = description
        self.done = done
        self.note = note
        self.task_id = task_id
        if task_type is not None:
            self.task_type = task_type

    def to_dict(self) -> dict[str, Any]:
        """
        Convert this task's shared fields to a JSON-ready dictionary.

        Returns:
        --------
        dict[str, Any]: The shared task fields and its type marker.
        """
        return {
            "task_id": self.task_id,
            "description": self.description,
            "done": self.done,
            "note": self.note,
            "task_type": self.task_type,
        }

    def __str__(self) -> str:
        """
        Format this task for display.

        Returns:
        --------
        str: The task type marker, completion status, and description,
            with timing information and a note when present.
        """
        return (
            f"{self._get_type_mark()}"
            f"{self._get_done_mark()}"
            f"{self.description}"
            f"{self._format_time_info()}"
            f"{self._format_note()}"
        )

    def _get_type_mark(self) -> str:
        """
        Return the display marker for this task's type.

        Returns:
        --------
        str: The type marker, or an empty string for an unrecognized type.
        """
        task_type_marks = {
            "todo": "[T]",
            "deadline": "[D]",
            "event": "[E]",
            "recurring": "[R]",
        }
        return task_type_marks.get(self.task_type, "")

    def _get_done_mark(self) -> str:
        """
        Return the display marker for this task's completion status.

        Returns:
        --------
        str: "[X]" if complete, otherwise "[ ]".
        """
        return "[X]" if self.done else "[ ]"

    def _format_note(self) -> str:
        """
        Format this task's note for display on a separate line.

        Returns:
        --------
        str: A leading newline and labeled note, or an empty string if absent.
        """
        return f"\nNote: {self.note}" if self.note else ""

    def _format_time_info(self) -> str:
        """
        Format timing information according to this task's type.

        Returns:
        --------
        str: The timing text with a leading space, or an empty string if absent.
        """

        recurrence_rule = getattr(self, "recurrence_rule", None)
        if recurrence_rule:
            return f" (every: {recurrence_rule})"

        due_date = getattr(self, "due_date", None)
        if due_date is not None:
            return f" (on: {due_date:%b %d %Y})"

        due_datetime = getattr(self, "due_datetime", None)
        if due_datetime is not None:
            deadline_text = due_datetime.strftime("%b %d %Y")

            if due_datetime.time() != time.min:
                hour = due_datetime.hour % 12 or 12
                minute = f":{due_datetime.minute:02d}" if due_datetime.minute else ""
                period = "am" if due_datetime.hour < 12 else "pm"
                deadline_text += f", {hour}{minute}{period}"

            return f" (by: {deadline_text})"

        start_datetime = getattr(self, "start_datetime", None)
        end_datetime = getattr(self, "end_datetime", None)
        if start_datetime and end_datetime:
            start_text = start_datetime.strftime("%Y-%m-%d %H:%M")
            end_text = end_datetime.strftime("%Y-%m-%d %H:%M")
            return f" (from: {start_text} to: {end_text})"

        return ""


class TodoTask(Task):
    """A task with an optional calendar date."""

    # Identity
    task_type = "todo"

    def __init__(
        self,
        description: str,
        due_date: date | None = None,
        done: bool = False,
        note: str | None = None,
        task_id: int | None = None,
    ) -> None:
        """Initialize a todo task with an optional date."""
        super().__init__(description, done=done, note=note, task_id=task_id)
        self.due_date = due_date

    def to_dict(self) -> dict[str, Any]:
        """Return shared and todo date fields."""
        task = super().to_dict()
        task["due_date"] = self.due_date.isoformat() if self.due_date else None
        return task


class DeadlineTask(Task):
    """A task with an optional due datetime."""

    # Identity
    task_type = "deadline"

    def __init__(
        self,
        description: str,
        due_datetime: datetime | None = None,
        done: bool = False,
        note: str | None = None,
        task_id: int | None = None,
    ) -> None:
        """Initialize a deadline task with its applicable fields."""
        # State
        super().__init__(description, done=done, note=note, task_id=task_id)
        self.due_datetime = due_datetime

    def to_dict(self) -> dict[str, Any]:
        """Return shared and deadline fields with ISO datetime values."""
        task = super().to_dict()
        task["due_datetime"] = (
            self.due_datetime.isoformat() if self.due_datetime is not None else None
        )
        return task


class EventTask(Task):
    """A task with optional event start and end datetimes."""

    # Identity
    task_type = "event"

    def __init__(
        self,
        description: str,
        start_datetime: datetime | None = None,
        end_datetime: datetime | None = None,
        done: bool = False,
        note: str | None = None,
        task_id: int | None = None,
    ) -> None:
        """Initialize an event task with its applicable fields."""
        # State
        super().__init__(description, done=done, note=note, task_id=task_id)
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime

    def to_dict(self) -> dict[str, Any]:
        """Return shared and event fields."""
        task = super().to_dict()
        task["start_datetime"] = (
            self.start_datetime.isoformat() if self.start_datetime is not None else None
        )
        task["end_datetime"] = (
            self.end_datetime.isoformat() if self.end_datetime is not None else None
        )
        return task


class RecurringTask(Task):
    """A task with a recurrence rule."""

    # Identity
    task_type = "recurring"

    def __init__(
        self,
        description: str,
        recurrence_rule: str | None = None,
        done: bool = False,
        note: str | None = None,
        task_id: int | None = None,
    ) -> None:
        """Initialize a recurring task with its applicable fields."""
        # State
        super().__init__(description, done=done, note=note, task_id=task_id)
        self.recurrence_rule = recurrence_rule

    def to_dict(self) -> dict[str, Any]:
        """Return shared and recurrence fields."""
        task = super().to_dict()
        task["recurrence_rule"] = self.recurrence_rule
        return task
