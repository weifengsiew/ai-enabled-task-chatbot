"""Individual task state and display formatting."""

from datetime import date, time


class Task:
    def __init__(self, description: str, task_type: str) -> None:
        """
        Initializes an incomplete task with no note or timing assigned.

        Args:
        -----
        description (str): What needs to be done.
        task_type (str): The task category: todo, deadline, event, or recurring.

        Returns:
        --------
        None.
        """
        self.description = description
        self.done = False
        self.note: str | None = None
        self.task_type = task_type
        self.day: str | None = None
        self.start: str | None = None
        self.end: str | None = None
        self.due_date: date | None = None
        self.due_time: time | None = None

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

    def add_note(self, note: str) -> None:
        """
        Stores a note on this task, replacing any existing note.

        Args:
        -----
        note (str): The note text to store.

        Returns:
        --------
        None.
        """
        self.note = note

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

        time_info = ""
        if self.task_type == "recurring" and self.day:
            time_info = f" (every: {self.day})"
        elif self.task_type == "deadline" and self.due_date is not None:
            deadline_text = self.due_date.strftime("%b %d %Y")

            if self.due_time is not None:
                hour = self.due_time.hour % 12 or 12
                minute = f":{self.due_time.minute:02d}" if self.due_time.minute else ""
                period = "am" if self.due_time.hour < 12 else "pm"
                deadline_text += f", {hour}{minute}{period}"

            time_info = f" (by: {deadline_text})"
        elif self.task_type == "event" and self.start and self.end:
            time_info = f" (from: {self.start} to: {self.end})"

        return time_info
