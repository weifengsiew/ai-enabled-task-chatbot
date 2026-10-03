"""Task models, task-specific state, and display formatting."""

from datetime import date, time
from typing import Any


class Task:
    """Shared state and behavior for every task type."""

    # Identity: each Task instance represents one distinct task object.
    task_type = ""

    def __init__(
        self,
        description: str,
        task_type: str | None = None,
        done: bool = False,
        note: str | None = None,
    ) -> None:
        """
        Initializes a task with its shared fields.

        Args:
        -----
        description (str): What needs to be done.
        task_type (str | None): An optional type marker for a generic task.
        done (bool): Whether the task is complete.
        note (str | None): An optional note attached to the task.

        Returns:
        --------
        None.
        """
        # State: these attributes describe the task's current condition.
        self.description = description
        self.done = done
        self.note = note
        if task_type is not None:
            self.task_type = task_type

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

    def __str__(self) -> str:
        """
        Formats this task for display.

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
        Returns the display marker for this task's type.

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
        Returns the display marker for this task's completion status.

        Returns:
        --------
        str: "[X]" if complete, otherwise "[ ]".
        """
        return "[X]" if self.done else "[ ]"

    def _format_note(self) -> str:
        """
        Formats this task's note for display on a separate line.

        Returns:
        --------
        str: A leading newline and labeled note, or an empty string if absent.
        """
        return f"\nNote: {self.note}" if self.note else ""

    def _format_time_info(self) -> str:
        """
        Formats timing information according to this task's type.

        Returns:
        --------
        str: The timing text with a leading space, or an empty string if absent.
        """

        day = getattr(self, "day", None)
        if day:
            return f" (every: {day})"

        due_date = getattr(self, "due_date", None)
        if due_date is not None:
            deadline_text = due_date.strftime("%b %d %Y")
            due_time = getattr(self, "due_time", None)

            if due_time is not None:
                hour = due_time.hour % 12 or 12
                minute = f":{due_time.minute:02d}" if due_time.minute else ""
                period = "am" if due_time.hour < 12 else "pm"
                deadline_text += f", {hour}{minute}{period}"

            return f" (by: {deadline_text})"

        start = getattr(self, "start", None)
        end = getattr(self, "end", None)
        if start and end:
            return f" (from: {start} to: {end})"

        return ""


class TodoTask(Task):
    """A task without type-specific timing fields."""

    task_type = "todo"


class DeadlineTask(Task):
    """A task with an optional due date and due time."""

    task_type = "deadline"

    def __init__(
        self,
        description: str,
        due_date: date | None = None,
        due_time: time | None = None,
        done: bool = False,
        note: str | None = None,
    ) -> None:
        """Initializes a deadline task with its applicable fields."""
        super().__init__(description, done=done, note=note)
        self.due_date = due_date
        self.due_time = due_time

    def to_dict(self) -> dict[str, Any]:
        """Returns shared and deadline fields with ISO date values."""
        task = super().to_dict()
        task["due_date"] = (
            self.due_date.isoformat() if self.due_date is not None else None
        )
        task["due_time"] = (
            self.due_time.isoformat() if self.due_time is not None else None
        )
        return task


class EventTask(Task):
    """A task with optional event start and end text."""

    task_type = "event"

    def __init__(
        self,
        description: str,
        start: str | None = None,
        end: str | None = None,
        done: bool = False,
        note: str | None = None,
    ) -> None:
        """Initializes an event task with its applicable fields."""
        super().__init__(description, done=done, note=note)
        self.start = start
        self.end = end

    def to_dict(self) -> dict[str, Any]:
        """Returns shared and event fields."""
        task = super().to_dict()
        task["start"] = self.start
        task["end"] = self.end
        return task


class RecurringTask(Task):
    """A task with an optional recurrence day."""

    task_type = "recurring"

    def __init__(
        self,
        description: str,
        day: str | None = None,
        done: bool = False,
        note: str | None = None,
    ) -> None:
        """Initializes a recurring task with its applicable field."""
        super().__init__(description, done=done, note=note)
        self.day = day

    def to_dict(self) -> dict[str, Any]:
        """Returns shared and recurrence fields."""
        task = super().to_dict()
        task["day"] = self.day
        return task
