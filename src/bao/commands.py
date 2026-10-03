"""Define the parent Command class and child classes CommandBye, CommandList,
CommandToDo, CommandDeadline, CommandEvent, CommandRecurring, CommandDue,
CommandFind, CommandMark, CommandUnmark, CommandNote, and CommandDelete.
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from datetime import UTC, datetime, time

from .display import (
    _format_missing_task_message,
    _get_task_by_number,
    _number_tasks_for_display,
)
from .parser import _parse_datetime_parts, _parse_number_command
from .task import DeadlineTask, EventTask, RecurringTask, TodoTask
from .tasks import Tasks

UNMATCHED_COMMAND_MESSAGE = ("Never heard of it. Try: todo, deadline, event, recurring, list, due, find, "
                             "mark, unmark, note, delete, bye.")

class Command(ABC):
    """Base class for commands that parse and execute user requests."""

    # Identity
    command_keyword: str
    command_pattern: re.Pattern[str]
    command_usage: str

    @classmethod
    def match_user_response_with_command_keyword(cls, user_response: str) -> bool:
        """Return whether user response matches command keyword."""
        
        matched_keyword = (user_response == cls.command_keyword
                           or user_response.startswith(f"{cls.command_keyword} "))
        return matched_keyword

    @classmethod
    def parse_user_response_with_command_pattern(cls, user_response: str) -> Command | str | None:
        """Find the matching command and parse one user response."""

        for command_class in COMMAND_CLASSES:
            matched_keyword = command_class.match_user_response_with_command_keyword(user_response)
            if matched_keyword:
                matched_command = command_class.parse_user_response_with_command_pattern(user_response)
                if matched_command is not None:
                    return matched_command
        return UNMATCHED_COMMAND_MESSAGE

    @abstractmethod
    def execute_command(self, tasks: Tasks) -> str:
        """Execute the command."""


class CommandBye(Command):
    """Terminate the conversation with Bao."""

    def __init__(self) -> None:
        # Identity
        self.command_keyword = "bye"
        self.command_pattern = re.compile(r"^bye$")
        self.command_usage = "bye"

    @classmethod
    def match_user_response_with_command_keyword(cls, user_response: str) -> bool:
        """Return whether user response matches command keyword."""

        command = cls()
        matched_keyword = (command.command_keyword == user_response
                           or user_response.startswith(f"{command.command_keyword} "))
        return matched_keyword

    @classmethod
    def parse_user_response_with_command_pattern(cls, user_response: str) -> CommandBye | None:
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
        # Identity
        self.command_keyword = "list"
        self.command_pattern = re.compile(r"^list$")
        self.command_usage = "list"
        self.task_count_summary_message = "That's {count} on your plate."

    @classmethod
    def match_user_response_with_command_keyword(cls, user_response: str) -> bool:
        """Return whether user response matches command keyword."""

        command = cls()
        matched_keyword = (command.command_keyword == user_response
                           or user_response.startswith(f"{command.command_keyword} "))
        return matched_keyword

    @classmethod
    def parse_user_response_with_command_pattern(cls, user_response: str) -> CommandList | None:
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


class CommandToDo(Command):
    """Add a todo task."""

    def __init__(self, task_description: str) -> None:
        # Identity
        self.command_keyword = "todo"
        self.command_usage = "todo <description>"
        self.command_pattern = re.compile(r"^todo\s+(.+)$")
        self.unmatched_command_pattern_message = "Use: todo <description>"
        self.success_message_prefix = "Added:"
        self.minimum_description_length = 1
        self.maximum_description_length = 500
        # State
        self.task_description = task_description

    @classmethod
    def match_user_response_with_command_keyword(cls, user_response: str) -> bool:
        """Return whether user response matches command keyword."""

        command = cls("")
        matched_keyword = (command.command_keyword == user_response
                           or user_response.startswith(f"{command.command_keyword} "))
        return matched_keyword

    @classmethod
    def parse_user_response_with_command_pattern(cls, user_response: str) -> Command | str | None:
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
        # Identity
        self.command_keyword = "deadline"
        self.command_usage = "deadline <description> /by YYYY-MM-DD [HHMM]"
        self.command_pattern = re.compile(r"^deadline\s+(.+?)\s+/by\s+(.+)$")
        self.unmatched_command_pattern_message = f"Use: {self.command_usage}"
        self.invalid_datetime_message = ("Invalid deadline. Use a valid date as YYYY-MM-DD, "
                                         "optionally followed by a time as HHMM (0000–2359).")
        self.success_message_prefix = "Added:"
        # State
        self.task_description = task_description
        self.due_datetime = due_datetime

    @classmethod
    def match_user_response_with_command_keyword(cls, user_response: str) -> bool:
        """Return whether user response matches command keyword."""

        minimum_datetime = datetime.min.replace(tzinfo=UTC)
        command = cls("", minimum_datetime)
        matched_keyword = (command.command_keyword == user_response
                           or user_response.startswith(f"{command.command_keyword} "))
        return matched_keyword

    @classmethod
    def parse_user_response_with_command_pattern(cls, user_response: str) -> CommandDeadline | str | None:
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

    def __init__(self, task_description: str, start_datetime: datetime, end_datetime: datetime) -> None:
        # Identity
        self.command_keyword = "event"
        self.command_usage = (
            "event <description> /from YYYY-MM-DD HHMM /to YYYY-MM-DD HHMM"
        )
        self.command_pattern = re.compile(r"^event\s+(.+?)\s+/from\s+(.+?)\s+/to\s+(.+)$")
        self.unmatched_command_pattern_message = f"Use: {self.command_usage}"
        self.invalid_datetime_message = "Invalid event date or time. Use YYYY-MM-DD HHMM."
        self.success_message_prefix = "Added:"
        # State
        self.task_description = task_description
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime

    @classmethod
    def match_user_response_with_command_keyword(cls, user_response: str) -> bool:
        """Return whether user response matches command keyword."""

        minimum_datetime = datetime.min.replace(tzinfo=UTC)
        command = cls("", minimum_datetime, minimum_datetime)
        matched_keyword = (command.command_keyword == user_response
                           or user_response.startswith(f"{command.command_keyword} "))
        return matched_keyword

    @classmethod
    def parse_user_response_with_command_pattern(cls, user_response: str) -> CommandEvent | str | None:
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

        task = EventTask(
            self.task_description, self.start_datetime, self.end_datetime
        )
        tasks.append(task)
        tasks.save()
        success_message = f"{self.success_message_prefix}\n{task}"
        return success_message


class CommandRecurring(Command):
    """Add a recurring task."""

    def __init__(self, task_description: str, recurrence_rule: str) -> None:
        # Identity
        self.command_keyword = "recurring"
        self.command_usage = "recurring <description> /every <rule>"
        self.command_pattern = re.compile(r"^recurring\s+(.+?)\s+/every\s+(.+)$")
        self.unmatched_command_pattern_message = f"Use: {self.command_usage}"
        self.success_message_prefix = "Added:"
        # State
        self.task_description = task_description
        self.recurrence_rule = recurrence_rule

    @classmethod
    def match_user_response_with_command_keyword(cls, user_response: str) -> bool:
        """Return whether user response matches command keyword."""

        command = cls("", "")
        matched_keyword = (command.command_keyword == user_response
                           or user_response.startswith(f"{command.command_keyword} "))
        return matched_keyword

    @classmethod
    def parse_user_response_with_command_pattern(cls, user_response: str) -> CommandRecurring | str | None:
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


class CommandDue(Command):
    """Find deadline tasks due on a date and optional time."""

    def __init__(self, query_datetime: datetime, query_has_time: bool) -> None:
        # Identity
        self.command_keyword = "due"
        self.command_usage = "due YYYY-MM-DD [HHMM]"
        self.command_pattern = re.compile(r"^due\s+(.+)$")
        self.unmatched_command_pattern_message = f"Use: {self.command_usage}"
        self.invalid_datetime_message = (
            "Invalid date or time. Use a valid date as YYYY-MM-DD, "
            "optionally followed by a time as HHMM (0000–2359)."
        )
        self.no_due_tasks_message = "No deadlines due on {datetime}."
        # State
        self.query_datetime = query_datetime
        self.query_has_time = query_has_time

    @classmethod
    def match_user_response_with_command_keyword(cls, user_response: str) -> bool:
        """Return whether user response matches command keyword."""

        minimum_datetime = datetime.min.replace(tzinfo=UTC)
        command = cls(minimum_datetime, False)
        matched_keyword = (command.command_keyword == user_response
                           or user_response.startswith(f"{command.command_keyword} "))
        return matched_keyword

    @classmethod
    def parse_user_response_with_command_pattern(cls, user_response: str) -> CommandDue | str | None:
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
            matched_command_pattern.group(1),)
        if matched_datetime_pattern is None:
            return command.unmatched_command_pattern_message
        
        parsed = _parse_datetime_parts(matched_command_pattern.group(1))
        if parsed is None:
            return command.invalid_datetime_message
        
        query_date, query_time = parsed
        query_datetime = datetime.combine(query_date, query_time or time.min, tzinfo=UTC)
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
            if not self.query_has_time and task_due_datetime.date() != self.query_datetime.date():
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
        # Identity
        self.command_keyword = "find"
        self.command_usage = "find <text>"
        self.command_pattern = re.compile(r"^find\s+(.+)$")
        self.unmatched_command_pattern_message = f"Use: {self.command_usage}"
        self.no_matching_tasks_message = 'No tasks found matching "{query}".'
        # State
        self.query = query

    @classmethod
    def match_user_response_with_command_keyword(cls, user_response: str) -> bool:
        """Return whether user response matches command keyword."""

        command = cls("")
        matched_keyword = (command.command_keyword == user_response
                           or user_response.startswith(f"{command.command_keyword} "))
        return matched_keyword

    @classmethod
    def parse_user_response_with_command_pattern(cls, user_response: str) -> CommandFind | str | None:
        """Return command if user response matches command pattern, else None."""

        matched_keyword = cls.match_user_response_with_command_keyword(user_response)
        if not matched_keyword:
            return None
        
        command = cls("")
        matched_command_pattern = command.command_pattern.fullmatch(user_response)
        if matched_command_pattern is None:
            return command.unmatched_command_pattern_message
        
        matched_description_pattern = re.fullmatch(
            r"\S(?:.*\S)?\s*", matched_command_pattern.group(1))
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


class CommandMark(Command):
    """Mark a task as done."""

    def __init__(self, task_number: int) -> None:
        # Identity
        self.command_keyword = "mark"
        self.command_usage = "mark <number>"
        self.command_pattern = re.compile(r"^mark\s+(.+)$")
        self.unmatched_command_pattern_message = f"Use: {self.command_usage}"
        self.success_message_prefix = "Done:"
        # State
        self.task_number = task_number

    @classmethod
    def match_user_response_with_command_keyword(cls, user_response: str) -> bool:
        """Return whether user response matches command keyword."""

        command = cls(0)
        matched_keyword = (command.command_keyword == user_response
                           or user_response.startswith(f"{command.command_keyword} "))
        return matched_keyword

    @classmethod
    def parse_user_response_with_command_pattern(cls, user_response: str) -> CommandMark | str | None:
        """Return command if user response matches command pattern, else None."""
        return _parse_number_command(cls(0), user_response)

    def execute_command(self, tasks: Tasks) -> str:
        """Execute the command."""

        task = _get_task_by_number(tasks, self.task_number)
        if task is None:
            return _format_missing_task_message(tasks, self.task_number)
        
        task.done = True
        tasks.save()

        success_message = f"{self.success_message_prefix}\n{task}"
        return success_message


class CommandUnmark(Command):
    """Mark a task as incomplete."""

    def __init__(self, task_number: int) -> None:
        # Identity
        self.command_keyword = "unmark"
        self.command_usage = "unmark <number>"
        self.command_pattern = re.compile(r"^unmark\s+(.+)$")
        self.unmatched_command_pattern_message = f"Use: {self.command_usage}"
        self.success_message_prefix = "Not done:"
        # State
        self.task_number = task_number

    @classmethod
    def match_user_response_with_command_keyword(cls, user_response: str) -> bool:
        """Return whether user response matches command keyword."""

        command = cls(0)
        matched_keyword = (command.command_keyword == user_response
                           or user_response.startswith(f"{command.command_keyword} "))
        return matched_keyword

    @classmethod
    def parse_user_response_with_command_pattern(cls, user_response: str) -> CommandUnmark | str | None:
        """Return command if user response matches command pattern, else None."""
        return _parse_number_command(cls(0), user_response)

    def execute_command(self, tasks: Tasks) -> str:
        """Execute the command."""

        task = _get_task_by_number(tasks, self.task_number)
        if task is None:
            return _format_missing_task_message(tasks, self.task_number)
        
        task.done = False
        tasks.save()

        success_message = f"{self.success_message_prefix}\n{task}"
        return success_message


class CommandNote(Command):
    """Replace a task's note."""

    def __init__(self, task_number: int, note: str) -> None:
        # Identity
        self.command_keyword = "note"
        self.command_usage = "note <number> <note>"
        self.command_pattern = re.compile(r"^note\s+(\d+)\s+(.+)$")
        self.unmatched_command_pattern_message = f"Use: {self.command_usage}"
        self.success_message_prefix = "Noted:"
        # State
        self.task_number = task_number
        self.note = note

    @classmethod
    def match_user_response_with_command_keyword(cls, user_response: str) -> bool:
        """Return whether user response matches command keyword."""

        command = cls(0, "")
        matched_keyword = (command.command_keyword == user_response
                           or user_response.startswith(f"{command.command_keyword} "))
        return matched_keyword

    @classmethod
    def parse_user_response_with_command_pattern(cls, user_response: str) -> CommandNote | str | None:
        """Return command if user response matches command pattern, else None."""
        matched_keyword = cls.match_user_response_with_command_keyword(user_response)
        if not matched_keyword:
            return None
        
        command = cls(0, "")
        matched_command_pattern = command.command_pattern.fullmatch(user_response)
        if matched_command_pattern is None:
            return command.unmatched_command_pattern_message
        
        parsed_command = cls(
            int(matched_command_pattern.group(1)), matched_command_pattern.group(2))
        return parsed_command

    def execute_command(self, tasks: Tasks) -> str:
        """Execute the command."""

        task = _get_task_by_number(tasks, self.task_number)
        if task is None:
            return _format_missing_task_message(tasks, self.task_number)
        
        task.note = self.note
        tasks.save()

        success_message = f"{self.success_message_prefix}\n{task}"
        return success_message


class CommandDelete(Command):
    """Delete a task."""

    def __init__(self, task_number: int) -> None:
        # Identity
        self.command_keyword = "delete"
        self.command_usage = "delete <number>"
        self.command_pattern = re.compile(r"^delete\s+(.+)$")
        self.unmatched_command_pattern_message = f"Use: {self.command_usage}"
        self.success_message_prefix = "Deleted:"
        # State
        self.task_number = task_number

    @classmethod
    def match_user_response_with_command_keyword(cls, user_response: str) -> bool:
        """Return whether user response matches command keyword."""

        command = cls(0)
        matched_keyword = (command.command_keyword == user_response
                           or user_response.startswith(f"{command.command_keyword} "))
        return matched_keyword

    @classmethod
    def parse_user_response_with_command_pattern(cls, user_response: str) -> CommandDelete | str | None:
        """Return command if user response matches command pattern, else None."""
        return _parse_number_command(cls(0), user_response)

    def execute_command(self, tasks: Tasks) -> str:
        """Execute the command."""

        task = _get_task_by_number(tasks, self.task_number)
        if task is None:
            return _format_missing_task_message(tasks, self.task_number)
        
        deleted_task = tasks.pop(self.task_number - 1)
        tasks.save()

        success_message = (f"{self.success_message_prefix}\n{deleted_task}\n{len(tasks)} tasks left.")
        return success_message


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
