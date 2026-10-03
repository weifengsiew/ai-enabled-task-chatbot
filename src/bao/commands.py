"""Command objects for Bao's interactive task management."""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from collections.abc import Iterable
from datetime import date, time

from .task import DeadlineTask, EventTask, RecurringTask, Task, TodoTask
from .tasks import Tasks

UNKNOWN_COMMAND = (
    "Never heard of it. Try: todo, deadline, event, recurring, list, due, find, "
    "mark, unmark, note, delete, bye."
)


class Command(ABC):
    """Common interface for validated user commands."""

    command_keyword: str
    command_pattern: re.Pattern[str]
    command_usage: str

    @classmethod
    def match_user_response_with_command_keyword(cls, user_response: str) -> bool:
        """Return whether user response matches command keyword."""
        matched_keyword = (
            user_response == cls.command_keyword
            or user_response.startswith(f"{cls.command_keyword} ")
        )
        return matched_keyword

    @classmethod
    def parse_user_response_with_command_pattern(
        cls, user_response: str
    ) -> Command | str | None:
        """Find the matching command and parse one user response."""
        for command_class in COMMAND_CLASSES:
            if command_class.match_user_response_with_command_keyword(user_response):
                parsed_command = command_class.parse_user_response_with_command_pattern(
                    user_response
                )
                if parsed_command is not None:
                    return parsed_command
        return UNKNOWN_COMMAND

    @abstractmethod
    def execute_command(self, tasks: Tasks) -> str:
        """Execute the command."""


class CommandBye(Command):
    """Terminate the conversation with Bao."""

    def __init__(self) -> None:
        self.command_keyword = "bye"
        self.command_pattern = re.compile(r"^bye$")
        self.command_usage = "bye"

    @classmethod
    def match_user_response_with_command_keyword(cls, user_response: str) -> bool:
        """Return whether user response matches command keyword."""
        command = cls()
        matched_keyword = (
            command.command_keyword == user_response
            or user_response.startswith(f"{command.command_keyword} ")
        )
        return matched_keyword

    @classmethod
    def parse_user_response_with_command_pattern(
        cls, user_response: str
    ) -> CommandBye | None:
        """Return command if user response matches command pattern, else None."""
        command = cls()
        matched_command = (
            command if command.command_pattern.fullmatch(user_response) else None
        )
        return matched_command

    def execute_command(self, tasks: Tasks) -> str:
        """Execute the command."""
        return ""


class CommandList(Command):
    """List all saved tasks."""

    def __init__(self) -> None:
        self.command_keyword = "list"
        self.command_pattern = re.compile(r"^list$")
        self.command_usage = "list"
        self.summary_message = "That's {count} on your plate."

    @classmethod
    def match_user_response_with_command_keyword(cls, user_response: str) -> bool:
        """Return whether user response matches command keyword."""
        command = cls()
        matched_keyword = (
            command.command_keyword == user_response
            or user_response.startswith(f"{command.command_keyword} ")
        )
        return matched_keyword

    @classmethod
    def parse_user_response_with_command_pattern(
        cls, user_response: str
    ) -> CommandList | None:
        """Return command if user response matches command pattern, else None."""
        command = cls()
        matched_command = (
            command if command.command_pattern.fullmatch(user_response) else None
        )
        return matched_command

    def execute_command(self, tasks: Tasks) -> str:
        """Execute the command."""
        messages = _number_tasks_for_display(tasks)
        incomplete_count = sum(1 for task in tasks if not task.done)
        messages.append(self.summary_message.format(count=incomplete_count))
        return "\n".join(messages)


class CommandToDo(Command):
    """Parse and execute a to-do command."""

    def __init__(self, task_description: str) -> None:
        self.command_keyword = "todo"
        self.command_usage = "todo <description>"
        self.command_pattern = re.compile(r"^todo\s+(.+)$")
        self.guidance_message = "Use: todo <description>"
        self.success_prefix = "Added:"
        self.minimum_description_length = 1
        self.maximum_description_length = 500
        self.task_description = task_description

    @classmethod
    def match_user_response_with_command_keyword(cls, user_response: str) -> bool:
        """Return whether user response matches command keyword."""
        command = cls("")
        matched_keyword = (
            command.command_keyword == user_response
            or user_response.startswith(f"{command.command_keyword} ")
        )
        return matched_keyword

    @classmethod
    def parse_user_response_with_command_pattern(
        cls, user_response: str
    ) -> CommandToDo | str | None:
        """Return command if user response matches command pattern, else None."""
        if not cls.match_user_response_with_command_keyword(user_response):
            return None

        command = cls("")
        match = command.command_pattern.fullmatch(user_response)
        if match is None:
            return command.guidance_message

        task_description = command.normalize_task_description(match.group(1))
        guidance = command.validate_task_description(task_description)
        if guidance is not None:
            return guidance
        return cls(task_description)

    def normalize_task_description(self, task_description: str) -> str:
        """Normalize whitespace in a to-do description."""
        return " ".join(task_description.split())

    def validate_task_description(self, task_description: str) -> str | None:
        """Return guidance when a to-do description is invalid."""
        if not (
            self.minimum_description_length
            <= len(task_description)
            <= self.maximum_description_length
        ):
            return self.guidance_message
        return None

    def execute_command(self, tasks: Tasks) -> str:
        """Execute the command."""
        task = TodoTask(self.task_description)
        tasks.append(task)
        tasks.save()
        return f"{self.success_prefix}\n{task}"

    def help_message(self) -> str:
        """Return usage guidance for the to-do command."""
        return self.guidance_message


class CommandDeadline(Command):
    """Create a task with a due date and optional due time."""

    def __init__(
        self, task_description: str, due_date: date, due_time: time | None
    ) -> None:
        self.command_keyword = "deadline"
        self.command_usage = "deadline <description> /by YYYY-MM-DD [HHMM]"
        self.command_pattern = re.compile(r"^deadline\s+(.+?)\s+/by\s+(.+)$")
        self.guidance_message = f"Use: {self.command_usage}"
        self.invalid_message = (
            "Invalid deadline. Use a valid date as YYYY-MM-DD, "
            "optionally followed by a time as HHMM (0000–2359)."
        )
        self.success_prefix = "Added:"
        self.task_description = task_description
        self.due_date = due_date
        self.due_time = due_time

    @classmethod
    def match_user_response_with_command_keyword(cls, user_response: str) -> bool:
        """Return whether user response matches command keyword."""
        command = cls("", date.min, None)
        matched_keyword = (
            command.command_keyword == user_response
            or user_response.startswith(f"{command.command_keyword} ")
        )
        return matched_keyword

    @classmethod
    def parse_user_response_with_command_pattern(
        cls, user_response: str
    ) -> CommandDeadline | str | None:
        """Return command if user response matches command pattern, else None."""
        if not cls.match_user_response_with_command_keyword(user_response):
            return None
        command = cls("", date.min, None)
        match = command.command_pattern.fullmatch(user_response)
        if match is None:
            return command.guidance_message
        parsed = _parse_deadline(match.group(2))
        if parsed is None:
            return command.invalid_message
        due_date, due_time = parsed
        return cls(match.group(1), due_date, due_time)

    def execute_command(self, tasks: Tasks) -> str:
        """Execute the command."""
        task = DeadlineTask(self.task_description, self.due_date, self.due_time)
        tasks.append(task)
        tasks.save()
        return f"{self.success_prefix}\n{task}"


class CommandEvent(Command):
    """Create an event task."""

    def __init__(self, task_description: str, start: str, end: str) -> None:
        self.command_keyword = "event"
        self.command_usage = "event <description> /from <start> /to <end>"
        self.command_pattern = re.compile(
            r"^event\s+(.+?)\s+/from\s+(.+?)\s+/to\s+(.+)$"
        )
        self.guidance_message = f"Use: {self.command_usage}"
        self.success_prefix = "Added:"
        self.task_description = task_description
        self.start = start
        self.end = end

    @classmethod
    def match_user_response_with_command_keyword(cls, user_response: str) -> bool:
        """Return whether user response matches command keyword."""
        command = cls("", "", "")
        matched_keyword = (
            command.command_keyword == user_response
            or user_response.startswith(f"{command.command_keyword} ")
        )
        return matched_keyword

    @classmethod
    def parse_user_response_with_command_pattern(
        cls, user_response: str
    ) -> CommandEvent | str | None:
        """Return command if user response matches command pattern, else None."""
        if not cls.match_user_response_with_command_keyword(user_response):
            return None
        command = cls("", "", "")
        match = command.command_pattern.fullmatch(user_response)
        if match is None:
            return command.guidance_message
        return cls(match.group(1), match.group(2), match.group(3))

    def execute_command(self, tasks: Tasks) -> str:
        """Execute the command."""
        task = EventTask(self.task_description, self.start, self.end)
        tasks.append(task)
        tasks.save()
        return f"{self.success_prefix}\n{task}"


class CommandRecurring(Command):
    """Create a recurring task."""

    def __init__(self, task_description: str, day: str) -> None:
        self.command_keyword = "recurring"
        self.command_usage = "recurring <description> /every <day>"
        self.command_pattern = re.compile(r"^recurring\s+(.+?)\s+/every\s+(\w+)$")
        self.guidance_message = f"Use: {self.command_usage}"
        self.success_prefix = "Added:"
        self.task_description = task_description
        self.day = day

    @classmethod
    def match_user_response_with_command_keyword(cls, user_response: str) -> bool:
        """Return whether user response matches command keyword."""
        command = cls("", "")
        matched_keyword = (
            command.command_keyword == user_response
            or user_response.startswith(f"{command.command_keyword} ")
        )
        return matched_keyword

    @classmethod
    def parse_user_response_with_command_pattern(
        cls, user_response: str
    ) -> CommandRecurring | str | None:
        """Return command if user response matches command pattern, else None."""
        if not cls.match_user_response_with_command_keyword(user_response):
            return None
        command = cls("", "")
        match = command.command_pattern.fullmatch(user_response)
        if match is None:
            return command.guidance_message
        return cls(match.group(1), match.group(2))

    def execute_command(self, tasks: Tasks) -> str:
        """Execute the command."""
        task = RecurringTask(self.task_description, self.day)
        tasks.append(task)
        tasks.save()
        return f"{self.success_prefix}\n{task}"


class CommandDue(Command):
    """Find deadline tasks due on a date."""

    def __init__(self, query_date: date) -> None:
        self.command_keyword = "due"
        self.command_usage = "due YYYY-MM-DD"
        self.command_pattern = re.compile(r"^due\s+(.+)$")
        self.guidance_message = f"Use: {self.command_usage}"
        self.invalid_message = "Invalid date. Use a valid calendar date as YYYY-MM-DD."
        self.empty_message = "No deadlines due on {date}."
        self.query_date = query_date

    @classmethod
    def match_user_response_with_command_keyword(cls, user_response: str) -> bool:
        """Return whether user response matches command keyword."""
        command = cls(date.min)
        matched_keyword = (
            command.command_keyword == user_response
            or user_response.startswith(f"{command.command_keyword} ")
        )
        return matched_keyword

    @classmethod
    def parse_user_response_with_command_pattern(
        cls, user_response: str
    ) -> CommandDue | str | None:
        """Return command if user response matches command pattern, else None."""
        if not cls.match_user_response_with_command_keyword(user_response):
            return None
        command = cls(date.min)
        match = command.command_pattern.fullmatch(user_response)
        if (
            match is None
            or re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", match.group(1)) is None
        ):
            return command.guidance_message
        try:
            return cls(date.fromisoformat(match.group(1)))
        except ValueError:
            return command.invalid_message

    def execute_command(self, tasks: Tasks) -> str:
        """Execute the command."""
        matches = [
            task for task in tasks if getattr(task, "due_date", None) == self.query_date
        ]
        if not matches:
            return self.empty_message.format(date=self.query_date)
        return "\n".join(_number_tasks_for_display(matches))


class CommandFind(Command):
    """Find tasks whose descriptions contain a query."""

    def __init__(self, query: str) -> None:
        self.command_keyword = "find"
        self.command_usage = "find <text>"
        self.command_pattern = re.compile(r"^find\s+(.+)$")
        self.guidance_message = f"Use: {self.command_usage}"
        self.empty_message = 'No tasks found matching "{query}".'
        self.query = query

    @classmethod
    def match_user_response_with_command_keyword(cls, user_response: str) -> bool:
        """Return whether user response matches command keyword."""
        command = cls("")
        matched_keyword = (
            command.command_keyword == user_response
            or user_response.startswith(f"{command.command_keyword} ")
        )
        return matched_keyword

    @classmethod
    def parse_user_response_with_command_pattern(
        cls, user_response: str
    ) -> CommandFind | str | None:
        """Return command if user response matches command pattern, else None."""
        if not cls.match_user_response_with_command_keyword(user_response):
            return None
        command = cls("")
        match = command.command_pattern.fullmatch(user_response)
        if match is None or re.fullmatch(r"\S(?:.*\S)?\s*", match.group(1)) is None:
            return command.guidance_message
        return cls(match.group(1).strip())

    def execute_command(self, tasks: Tasks) -> str:
        """Execute the command."""
        search_text = self.query.casefold()
        matches = [task for task in tasks if search_text in task.description.casefold()]
        if not matches:
            return self.empty_message.format(query=self.query)
        return "\n".join(_number_tasks_for_display(matches))


class CommandMark(Command):
    """Mark a task as done."""

    def __init__(self, task_number: int) -> None:
        self.command_keyword = "mark"
        self.command_usage = "mark <number>"
        self.command_pattern = re.compile(r"^mark\s+(.+)$")
        self.guidance_message = f"Use: {self.command_usage}"
        self.success_prefix = "Done:"
        self.task_number = task_number

    @classmethod
    def match_user_response_with_command_keyword(cls, user_response: str) -> bool:
        """Return whether user response matches command keyword."""
        command = cls(0)
        matched_keyword = (
            command.command_keyword == user_response
            or user_response.startswith(f"{command.command_keyword} ")
        )
        return matched_keyword

    @classmethod
    def parse_user_response_with_command_pattern(
        cls, user_response: str
    ) -> CommandMark | str | None:
        """Return command if user response matches command pattern, else None."""
        return _parse_number_command(cls(0), user_response)

    def execute_command(self, tasks: Tasks) -> str:
        """Execute the command."""
        task = _get_task_by_number(tasks, self.task_number)
        if task is None:
            return _format_missing_task_message(tasks, self.task_number)
        task.done = True
        tasks.save()
        return f"{self.success_prefix}\n{task}"


class CommandUnmark(Command):
    """Mark a task as incomplete."""

    def __init__(self, task_number: int) -> None:
        self.command_keyword = "unmark"
        self.command_usage = "unmark <number>"
        self.command_pattern = re.compile(r"^unmark\s+(.+)$")
        self.guidance_message = f"Use: {self.command_usage}"
        self.success_prefix = "Not done:"
        self.task_number = task_number

    @classmethod
    def match_user_response_with_command_keyword(cls, user_response: str) -> bool:
        """Return whether user response matches command keyword."""
        command = cls(0)
        matched_keyword = (
            command.command_keyword == user_response
            or user_response.startswith(f"{command.command_keyword} ")
        )
        return matched_keyword

    @classmethod
    def parse_user_response_with_command_pattern(
        cls, user_response: str
    ) -> CommandUnmark | str | None:
        """Return command if user response matches command pattern, else None."""
        return _parse_number_command(cls(0), user_response)

    def execute_command(self, tasks: Tasks) -> str:
        """Execute the command."""
        task = _get_task_by_number(tasks, self.task_number)
        if task is None:
            return _format_missing_task_message(tasks, self.task_number)
        task.done = False
        tasks.save()
        return f"{self.success_prefix}\n{task}"


class CommandNote(Command):
    """Replace a task's note."""

    def __init__(self, task_number: int, note: str) -> None:
        self.command_keyword = "note"
        self.command_usage = "note <number> <note>"
        self.command_pattern = re.compile(r"^note\s+(\d+)\s+(.+)$")
        self.guidance_message = f"Use: {self.command_usage}"
        self.success_prefix = "Noted:"
        self.task_number = task_number
        self.note = note

    @classmethod
    def match_user_response_with_command_keyword(cls, user_response: str) -> bool:
        """Return whether user response matches command keyword."""
        command = cls(0, "")
        matched_keyword = (
            command.command_keyword == user_response
            or user_response.startswith(f"{command.command_keyword} ")
        )
        return matched_keyword

    @classmethod
    def parse_user_response_with_command_pattern(
        cls, user_response: str
    ) -> CommandNote | str | None:
        """Return command if user response matches command pattern, else None."""
        if not cls.match_user_response_with_command_keyword(user_response):
            return None
        command = cls(0, "")
        match = command.command_pattern.fullmatch(user_response)
        if match is None:
            return command.guidance_message
        return cls(int(match.group(1)), match.group(2))

    def execute_command(self, tasks: Tasks) -> str:
        """Execute the command."""
        task = _get_task_by_number(tasks, self.task_number)
        if task is None:
            return _format_missing_task_message(tasks, self.task_number)
        task.note = self.note
        tasks.save()
        return f"{self.success_prefix}\n{task}"


class CommandDelete(Command):
    """Delete a task."""

    def __init__(self, task_number: int) -> None:
        self.command_keyword = "delete"
        self.command_usage = "delete <number>"
        self.command_pattern = re.compile(r"^delete\s+(.+)$")
        self.guidance_message = f"Use: {self.command_usage}"
        self.success_prefix = "Deleted:"
        self.task_number = task_number

    @classmethod
    def match_user_response_with_command_keyword(cls, user_response: str) -> bool:
        """Return whether user response matches command keyword."""
        command = cls(0)
        matched_keyword = (
            command.command_keyword == user_response
            or user_response.startswith(f"{command.command_keyword} ")
        )
        return matched_keyword

    @classmethod
    def parse_user_response_with_command_pattern(
        cls, user_response: str
    ) -> CommandDelete | str | None:
        """Return command if user response matches command pattern, else None."""
        return _parse_number_command(cls(0), user_response)

    def execute_command(self, tasks: Tasks) -> str:
        """Execute the command."""
        task = _get_task_by_number(tasks, self.task_number)
        if task is None:
            return _format_missing_task_message(tasks, self.task_number)
        deleted_task = tasks.pop(self.task_number - 1)
        tasks.save()
        return f"{self.success_prefix}\n{deleted_task}\n{len(tasks)} tasks left."


def _parse_number_command[NumberCommand: CommandMark | CommandUnmark | CommandDelete](
    command: NumberCommand,
    user_response: str,
) -> NumberCommand | str | None:
    """Parse a command that accepts one task number."""
    if not command.match_user_response_with_command_keyword(user_response):
        return None
    match = command.command_pattern.fullmatch(user_response)
    if match is None or re.fullmatch(r"\d+", match.group(1)) is None:
        return command.guidance_message
    command.task_number = int(match.group(1))
    return command


def _parse_deadline(value: str) -> tuple[date, time | None] | None:
    """Parse an ISO date and optional four-digit time."""
    match = re.fullmatch(r"([0-9]{4}-[0-9]{2}-[0-9]{2})(?:\s+([0-9]{4}))?", value)
    if match is None:
        return None
    try:
        due_date = date.fromisoformat(match.group(1))
        time_text = match.group(2)
        due_time = (
            time(hour=int(time_text[:2]), minute=int(time_text[2:]))
            if time_text is not None
            else None
        )
    except ValueError:
        return None
    return due_date, due_time


def _number_tasks_for_display(tasks: Iterable[object]) -> list[str]:
    """Format tasks with one-based display numbering."""
    return [f"{number}. {task}" for number, task in enumerate(tasks, start=1)]


def _format_missing_task_message(tasks: Tasks, task_number: int) -> str:
    """Format the guidance for a missing task number."""
    if len(tasks) > 0:
        message = f"Choose a number from 1 to {len(tasks)}."
    else:
        message = "There are no tasks yet."
    return f"No task {task_number}. {message}"


def _get_task_by_number(tasks: Tasks, task_number: int) -> Task | None:
    """Return a task by its task_number, if it exists."""
    if 1 <= task_number <= len(tasks):
        return tasks[task_number - 1]
    return None


COMMAND_CLASSES: tuple[type[Command], ...] = (
    CommandBye,
    CommandList,
    CommandToDo,
    CommandDeadline,
    CommandEvent,
    CommandRecurring,
    CommandDue,
    CommandFind,
    CommandMark,
    CommandUnmark,
    CommandNote,
    CommandDelete,
)
