"""Define the command framework and lifecycle command."""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from collections.abc import Iterable
from datetime import UTC, datetime, time

from .parser import _parse_datetime_parts
from .task import Task
from .tasks import Tasks

UNMATCHED_COMMAND_MESSAGE = (
    "Never heard of it. Try: todo, deadline, event, recurring, list, due, find, "
    "filter, mark, unmark, note, delete, bye."
)

TASK_TYPES = ("todo", "deadline", "event", "recurring")


def _number_tasks_for_display(tasks: Iterable[object]) -> list[str]:
    """Format tasks with one-based display numbering."""

    return [f"{number}. {task}" for number, task in enumerate(tasks, start=1)]


def _format_missing_task_message(tasks: Tasks, task_number: int) -> str:
    """Format guidance for a missing task number."""

    if len(tasks) > 0:
        message = f"Choose a number from 1 to {len(tasks)}."
    else:
        message = "There are no tasks yet."
    missing_task_message = f"No task {task_number}. {message}"
    return missing_task_message


def _get_task_by_number(tasks: Tasks, task_number: int) -> Task | None:
    """Return a task by its one-based number, if it exists."""

    if 1 <= task_number <= len(tasks):
        return tasks[task_number - 1]
    return None


class Command(ABC):
    """Base class for commands that parse and execute user requests."""

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
            matched_keyword = command_class.match_user_response_with_command_keyword(
                user_response
            )
            if matched_keyword:
                matched_command = (
                    command_class.parse_user_response_with_command_pattern(
                        user_response
                    )
                )
                if matched_command is not None:
                    return matched_command
        return UNMATCHED_COMMAND_MESSAGE

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
        matched_pattern = command.command_pattern.fullmatch(user_response)
        matched_command = command if matched_pattern else None
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
        self.task_count_summary_message = "That's {count} on your plate."

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
        matched_pattern = command.command_pattern.fullmatch(user_response)
        matched_command = command if matched_pattern else None
        return matched_command

    def execute_command(self, tasks: Tasks) -> str:
        """Execute the command."""

        numbered_tasks = _number_tasks_for_display(tasks)
        incomplete_count = sum(1 for task in tasks if not task.done)
        numbered_tasks.append(
            self.task_count_summary_message.format(count=incomplete_count)
        )
        task_list_message = "\n".join(numbered_tasks)
        return task_list_message


class CommandDue(Command):
    """Find deadline tasks due on a date and optional time."""

    def __init__(self, query_datetime: datetime, query_has_time: bool) -> None:
        self.command_keyword = "due"
        self.command_usage = "due YYYY-MM-DD [HHMM]"
        self.command_pattern = re.compile(r"^due\s+(.+)$")
        self.unmatched_command_pattern_message = f"Use: {self.command_usage}"
        self.invalid_datetime_message = (
            "Invalid date or time. Use a valid date as YYYY-MM-DD, "
            "optionally followed by a time as HHMM (0000–2359)."
        )
        self.no_due_tasks_message = "No deadlines due on {datetime}."
        self.query_datetime = query_datetime
        self.query_has_time = query_has_time

    @classmethod
    def match_user_response_with_command_keyword(cls, user_response: str) -> bool:
        """Return whether user response matches command keyword."""

        minimum_datetime = datetime.min.replace(tzinfo=UTC)
        command = cls(minimum_datetime, False)
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

        matched_keyword = cls.match_user_response_with_command_keyword(user_response)
        if not matched_keyword:
            return None

        minimum_datetime = datetime.min.replace(tzinfo=UTC)
        command = cls(minimum_datetime, False)
        matched_command_pattern = command.command_pattern.fullmatch(user_response)
        if matched_command_pattern is None:
            return command.unmatched_command_pattern_message

        matched_datetime_pattern = re.fullmatch(
            r"[0-9]{4}-[0-9]{2}-[0-9]{2}(?:\s+[0-9]{4})?",
            matched_command_pattern.group(1),
        )
        if matched_datetime_pattern is None:
            return command.unmatched_command_pattern_message

        parsed = _parse_datetime_parts(matched_command_pattern.group(1))
        if parsed is None:
            return command.invalid_datetime_message

        query_date, query_time = parsed
        query_datetime = datetime.combine(
            query_date, query_time or time.min, tzinfo=UTC
        )
        query_has_time = query_time is not None
        parsed_command = cls(query_datetime, query_has_time)
        return parsed_command

    def execute_command(self, tasks: Tasks) -> str:
        """Execute the command."""

        matches = []
        for task in tasks:
            task_due_datetime = getattr(task, "due_datetime", None)
            if task_due_datetime is None:
                continue
            if self.query_has_time and task_due_datetime != self.query_datetime:
                continue
            if (
                not self.query_has_time
                and task_due_datetime.date() != self.query_datetime.date()
            ):
                continue
            matches.append(task)

        if not matches:
            query_text = self.query_datetime.strftime("%Y-%m-%d")
            if self.query_has_time:
                query_text += f" {self.query_datetime.strftime('%H%M')}"
            no_due_tasks_message = self.no_due_tasks_message.format(datetime=query_text)
            return no_due_tasks_message

        numbered_tasks = _number_tasks_for_display(matches)
        numbered_tasks_message = "\n".join(numbered_tasks)
        return numbered_tasks_message


class CommandFind(Command):
    """Find tasks whose descriptions contain a query."""

    def __init__(self, query: str) -> None:
        self.command_keyword = "find"
        self.command_usage = "find <text>"
        self.command_pattern = re.compile(r"^find\s+(.+)$")
        self.unmatched_command_pattern_message = f"Use: {self.command_usage}"
        self.no_matching_tasks_message = 'No tasks found matching "{query}".'
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

        matched_keyword = cls.match_user_response_with_command_keyword(user_response)
        if not matched_keyword:
            return None

        command = cls("")
        matched_command_pattern = command.command_pattern.fullmatch(user_response)
        if matched_command_pattern is None:
            return command.unmatched_command_pattern_message

        matched_description_pattern = re.fullmatch(
            r"\S(?:.*\S)?\s*", matched_command_pattern.group(1)
        )
        if matched_description_pattern is None:
            return command.unmatched_command_pattern_message

        parsed_command = cls(matched_command_pattern.group(1).strip())
        return parsed_command

    def execute_command(self, tasks: Tasks) -> str:
        """Execute the command."""

        search_text = self.query.casefold()
        matches = [task for task in tasks if search_text in task.description.casefold()]
        if not matches:
            return self.no_matching_tasks_message.format(query=self.query)

        numbered_tasks = _number_tasks_for_display(matches)
        numbered_tasks_message = "\n".join(numbered_tasks)
        return numbered_tasks_message


class CommandFilter(Command):
    """Find tasks of one type."""

    def __init__(self, task_type: str) -> None:
        self.command_keyword = "filter"
        self.command_usage = "filter <type>"
        self.command_pattern = re.compile(r"^filter\s+(.+)$")
        self.unmatched_command_pattern_message = f"Use: {self.command_usage}"
        self.no_matching_tasks_message = f'No tasks found of type "{task_type}".'
        self.task_type = task_type

    @classmethod
    def match_user_response_with_command_keyword(cls, user_response: str) -> bool:
        """Return whether user response matches command keyword."""

        command = cls(TASK_TYPES[0])
        matched_keyword = (
            command.command_keyword == user_response
            or user_response.startswith(f"{command.command_keyword} ")
        )
        return matched_keyword

    @classmethod
    def parse_user_response_with_command_pattern(
        cls, user_response: str
    ) -> CommandFilter | str | None:
        """Return command if user response matches command pattern, else None."""

        matched_keyword = cls.match_user_response_with_command_keyword(user_response)
        if not matched_keyword:
            return None

        command = cls(TASK_TYPES[0])
        matched_command_pattern = command.command_pattern.fullmatch(user_response)
        if matched_command_pattern is None:
            return command.unmatched_command_pattern_message

        task_type = matched_command_pattern.group(1)
        if task_type not in TASK_TYPES:
            return command.unmatched_command_pattern_message

        return cls(task_type)

    def execute_command(self, tasks: Tasks) -> str:
        """Execute the command."""

        matches = [task for task in tasks if task.task_type == self.task_type]
        if not matches:
            return self.no_matching_tasks_message

        numbered_tasks = _number_tasks_for_display(matches)
        numbered_tasks_message = "\n".join(numbered_tasks)
        return numbered_tasks_message


from .add_task_commands import (
    CommandDeadline,
    CommandEvent,
    CommandRecurring,
    CommandToDo,
)
from .modify_task_commands import (
    CommandDelete,
    CommandMark,
    CommandNote,
    CommandUnmark,
)

COMMAND_CLASSES: tuple[type[Command], ...] = (
    CommandBye,
    CommandList,
    CommandToDo,
    CommandDeadline,
    CommandEvent,
    CommandRecurring,
    CommandDue,
    CommandFind,
    CommandFilter,
    CommandMark,
    CommandUnmark,
    CommandNote,
    CommandDelete,
)
