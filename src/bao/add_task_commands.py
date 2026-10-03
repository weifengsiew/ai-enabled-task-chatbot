"""Define commands that create tasks."""

from __future__ import annotations

import re
from datetime import UTC, datetime, time

from .parser import _parse_datetime_parts
from .read_task_commands import Command
from .task import DeadlineTask, EventTask, RecurringTask, TodoTask
from .tasks import Tasks


class CommandToDo(Command):
    """Add a todo task."""

    def __init__(self, task_description: str) -> None:
        self.command_keyword = "todo"
        self.command_usage = "todo <description>"
        self.command_pattern = re.compile(r"^todo\s+(.+)$")
        self.unmatched_command_pattern_message = "Use: todo <description>"
        self.success_message_prefix = "Added:"
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
    ) -> Command | str | None:
        """Return command if user response matches command pattern, else None."""

        matched_keyword = cls.match_user_response_with_command_keyword(user_response)
        if not matched_keyword:
            return None

        command = cls("")
        matched_command_pattern = command.command_pattern.fullmatch(user_response)
        if matched_command_pattern is None:
            return command.unmatched_command_pattern_message

        parsed_command = cls(matched_command_pattern.group(1))
        return parsed_command

    def execute_command(self, tasks: Tasks) -> str:
        """Execute the command."""

        task = TodoTask(self.task_description)
        tasks.append(task)
        tasks.save()
        success_message = f"{self.success_message_prefix}\n{task}"
        return success_message


class CommandDeadline(Command):
    """Add a deadline task."""

    def __init__(self, task_description: str, due_datetime: datetime) -> None:
        self.command_keyword = "deadline"
        self.command_usage = "deadline <description> /by YYYY-MM-DD [HHMM]"
        self.command_pattern = re.compile(r"^deadline\s+(.+?)\s+/by\s+(.+)$")
        self.unmatched_command_pattern_message = f"Use: {self.command_usage}"
        self.invalid_datetime_message = (
            "Invalid deadline. Use a valid date as YYYY-MM-DD, "
            "optionally followed by a time as HHMM (0000–2359)."
        )
        self.success_message_prefix = "Added:"
        self.task_description = task_description
        self.due_datetime = due_datetime

    @classmethod
    def match_user_response_with_command_keyword(cls, user_response: str) -> bool:
        """Return whether user response matches command keyword."""

        minimum_datetime = datetime.min.replace(tzinfo=UTC)
        command = cls("", minimum_datetime)
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

        matched_keyword = cls.match_user_response_with_command_keyword(user_response)
        if not matched_keyword:
            return None

        minimum_datetime = datetime.min.replace(tzinfo=UTC)
        command = cls("", minimum_datetime)
        matched_command_pattern = command.command_pattern.fullmatch(user_response)
        if matched_command_pattern is None:
            return command.unmatched_command_pattern_message

        parsed = _parse_datetime_parts(matched_command_pattern.group(2))
        if parsed is None:
            return command.invalid_datetime_message

        due_date, due_time = parsed
        due_datetime = datetime.combine(due_date, due_time or time.min, tzinfo=UTC)
        parsed_command = cls(matched_command_pattern.group(1), due_datetime)
        return parsed_command

    def execute_command(self, tasks: Tasks) -> str:
        """Execute the command."""

        task = DeadlineTask(self.task_description, self.due_datetime)
        tasks.append(task)
        tasks.save()
        success_message = f"{self.success_message_prefix}\n{task}"
        return success_message


class CommandEvent(Command):
    """Add an event task."""

    def __init__(
        self, task_description: str, start_datetime: datetime, end_datetime: datetime
    ) -> None:
        self.command_keyword = "event"
        self.command_usage = (
            "event <description> /from YYYY-MM-DD HHMM /to YYYY-MM-DD HHMM"
        )
        self.command_pattern = re.compile(
            r"^event\s+(.+?)\s+/from\s+(.+?)\s+/to\s+(.+)$"
        )
        self.unmatched_command_pattern_message = f"Use: {self.command_usage}"
        self.invalid_datetime_message = (
            "Invalid event date or time. Use YYYY-MM-DD HHMM."
        )
        self.success_message_prefix = "Added:"
        self.task_description = task_description
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime

    @classmethod
    def match_user_response_with_command_keyword(cls, user_response: str) -> bool:
        """Return whether user response matches command keyword."""

        minimum_datetime = datetime.min.replace(tzinfo=UTC)
        command = cls("", minimum_datetime, minimum_datetime)
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

        matched_keyword = cls.match_user_response_with_command_keyword(user_response)
        if not matched_keyword:
            return None

        minimum_datetime = datetime.min.replace(tzinfo=UTC)
        command = cls("", minimum_datetime, minimum_datetime)
        matched_command_pattern = command.command_pattern.fullmatch(user_response)
        if matched_command_pattern is None:
            return command.unmatched_command_pattern_message
        start_parts = _parse_datetime_parts(matched_command_pattern.group(2))
        end_parts = _parse_datetime_parts(matched_command_pattern.group(3))
        if start_parts is None or end_parts is None:
            return command.invalid_datetime_message
        start_date, start_time = start_parts
        end_date, end_time = end_parts
        start_datetime = datetime.combine(
            start_date, start_time or time.min, tzinfo=UTC
        )
        end_datetime = datetime.combine(end_date, end_time or time.min, tzinfo=UTC)
        parsed_command = cls(
            matched_command_pattern.group(1),
            start_datetime,
            end_datetime,
        )
        return parsed_command

    def execute_command(self, tasks: Tasks) -> str:
        """Execute the command."""

        task = EventTask(self.task_description, self.start_datetime, self.end_datetime)
        tasks.append(task)
        tasks.save()
        success_message = f"{self.success_message_prefix}\n{task}"
        return success_message


class CommandRecurring(Command):
    """Add a recurring task."""

    def __init__(self, task_description: str, recurrence_rule: str) -> None:
        self.command_keyword = "recurring"
        self.command_usage = "recurring <description> /every <rule>"
        self.command_pattern = re.compile(r"^recurring\s+(.+?)\s+/every\s+(.+)$")
        self.unmatched_command_pattern_message = f"Use: {self.command_usage}"
        self.success_message_prefix = "Added:"
        self.task_description = task_description
        self.recurrence_rule = recurrence_rule

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

        matched_keyword = cls.match_user_response_with_command_keyword(user_response)
        if not matched_keyword:
            return None

        command = cls("", "")
        matched_command_pattern = command.command_pattern.fullmatch(user_response)
        if matched_command_pattern is None:
            return command.unmatched_command_pattern_message

        parsed_command = cls(
            matched_command_pattern.group(1),
            matched_command_pattern.group(2),
        )
        return parsed_command

    def execute_command(self, tasks: Tasks) -> str:
        """Execute the command."""

        task = RecurringTask(self.task_description, self.recurrence_rule)
        tasks.append(task)
        tasks.save()
        success_message = f"{self.success_message_prefix}\n{task}"
        return success_message
