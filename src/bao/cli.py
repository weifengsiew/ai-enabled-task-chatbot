"""Command-line entry point for bao."""
<<<<<<< HEAD
import json
=======
from datetime import date, datetime, time
>>>>>>> stage-8
import re
from pathlib import Path

def greeting() -> None:
    """
    Prints Bao's opening greeting to the terminal.

    Returns:
    --------
    None.
    """
    print("Hello! I'm bao. What needs doing?")

def farewell() -> None:
    """
    Prints Bao's closing message to the terminal.

    Returns:
    --------
    None.
    """
    print("Later.")
    
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
        self.note = None
        self.task_type = task_type
        self.day = None
<<<<<<< HEAD
        self.start: str | None = None
        self.end: str | None = None
=======
        self.due_date: date | None = None
        self.due_time: time | None = None
>>>>>>> stage-8

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
            "recurring": "[R]"}
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
                minute = (
                    f":{self.due_time.minute:02d}"
                    if self.due_time.minute
                    else ""
                )
                period = "am" if self.due_time.hour < 12 else "pm"
                deadline_text += f", {hour}{minute}{period}"

            time_info = f" (by: {deadline_text})"
        elif self.task_type == "event" and self.start and self.end:
            time_info = f" (from: {self.start} to: {self.end})"

        return time_info

class Tasks:
    def __init__(self) -> None:
        """
        Loads saved tasks, creating an empty save file on the first run.

        Returns:
        --------
        None.
        """
        self.tasks: list[Task] = []
        self._load_tasks()

    def _save_tasks(self) -> None:
        """
        Saves the task list to data/tasks.json.
        Creates the data directory if needed.

        Returns:
        --------
        None.
        """
        path = Path("data/tasks.json")
        path.parent.mkdir(parents=True, exist_ok=True)

        records = []
        for task in self.tasks:
            records.append({
                "description": task.description,
                "task_type": task.task_type,
                "done": task.done,
                "note": task.note,
                "day": task.day,
                "start": task.start,
                "end": task.end,
            })

        path.write_text(json.dumps(records, indent=2), encoding="utf-8")

    def _load_tasks(self) -> None:
        """
        Loads the task list from data/tasks.json.
        Creates an empty save file if it does not exist.

        Returns:
        --------
        None.
        """
        path = Path("data/tasks.json")
        if not path.exists():
            self._save_tasks()
            return

        records = json.loads(path.read_text(encoding="utf-8"))
        loaded_tasks = []

        for record in records:
            task = Task(record["description"], record["task_type"])
            task.done = record["done"]
            task.note = record["note"]
            task.day = record["day"]
            task.start = record.get("start")
            task.end = record.get("end")
            loaded_tasks.append(task)

        self.tasks = loaded_tasks

    @staticmethod
    def _match_user_response(
        user_response: str,
        pattern: str,
        usage: str,
    ) -> re.Match[str] | None:
        """
        Matches the entire command against a regex pattern.
        Prints the usage message if the command does not match.

        Args:
        -----
        user_response (str): The command text to check.
        pattern (str): The regex pattern defining the expected command format.
        usage (str): The message to print when the command is invalid.

        Returns:
        --------
        re.Match[str] | None: The match containing captured fields,
            or None if the command does not match.
        """
        user_response_match = re.fullmatch(pattern, user_response)
        if user_response_match is None:
            print(usage)
        return user_response_match

    def _check_task_number(self, task_number: int) -> bool:
        """
        Checks whether a task number refers to an existing task.
        Prints guidance if the number is invalid.

        Args:
        -----
        task_number (int): The task's position in the list, starting at 1.

        Returns:
        --------
        bool: True if the task exists, otherwise False.
        """
        if 1 <= task_number <= len(self.tasks):
            return True

        if self.tasks:
            message = f"Choose a number from 1 to {len(self.tasks)}."
        else:
            message = "There are no tasks yet."

        print(f"No task {task_number}. {message}")
        return False

    def _append_task(self, task: Task) -> None:
        """
        Appends a task to the collection, saves it, and prints confirmation.

        Args:
        -----
        task (Task): The task to add to the collection.

        Returns:
        --------
        None.
        """
        self.tasks.append(task)
        self._save_tasks()
        print(f"Added:\n{task}")

    def _add_todo_task(self, user_response: str) -> None:
        """
        Creates and adds a todo task from command text.
        Prints confirmation on success, or usage guidance for invalid input.

        Args:
        -----
        user_response (str): A command in the format "todo <description>".

        Returns:
        --------
        None.
        """
        user_response_match = self._match_user_response(
            user_response,
            r"^todo\s+(.+)$",
            "Use: todo <description>",
        )

        if user_response_match is None:
            return

        description = user_response_match.group(1)

        task = Task(description, "todo")
        self._append_task(task)
    
    def _add_recurring_task(self, user_response: str) -> None:
        """
        Creates and adds a recurring task from command text.
        Prints confirmation on success, or usage guidance for invalid input.

        Args:
        -----
        user_response (str): A command in the format
            "recurring <description> /every <day>".

        Returns:
        --------
        None.
        """
        user_response_match = self._match_user_response(
            user_response,
            r"^recurring\s+(.+?)\s+/every\s+(\w+)$",
            "Use: recurring <description> /every <day>",
        )

        if user_response_match is None:
            return

        description = user_response_match.group(1)
        day = user_response_match.group(2)

        task = Task(description, "recurring")
        task.day = day

        self._append_task(task)

    @staticmethod
    def _parse_deadline(value: str) -> tuple[date, time | None] | None:
        """
        Converts deadline text into a date and optional time.
        Prints guidance if the format or value is invalid.

        Args:
        -----
        value (str): A date as YYYY-MM-DD, optionally followed by HHMM.

        Returns:
        --------
        tuple[date, time | None] | None: The parsed date and optional time,
            or None if invalid.
        """
        deadline_match = re.fullmatch(
            r"([0-9]{4}-[0-9]{2}-[0-9]{2})(?:\s+([0-9]{4}))?",
            value,
        )

        if deadline_match is not None:
            try:
                due_date = date.fromisoformat(deadline_match.group(1))
                time_text = deadline_match.group(2)
                due_time = (
                    datetime.strptime(time_text, "%H%M").time()
                    if time_text is not None
                    else None
                )
                return due_date, due_time
            except ValueError:
                pass

        print(
            "Invalid deadline. Use a valid date as YYYY-MM-DD, "
            "optionally followed by a time as HHMM (0000–2359)."
        )
        return None

    def _add_deadline_task(self, user_response: str) -> None:
        """
        Creates and adds a deadline task from command text.
        Prints confirmation on success, or guidance for invalid input.

        Args:
        -----
        user_response (str): A command in the format
            "deadline <description> /by YYYY-MM-DD [HHMM]".

        Returns:
        --------
        None.
        """
        user_response_match = self._match_user_response(
            user_response,
            r"^deadline\s+(.+?)\s+/by\s+(.+)$",
            "Use: deadline <description> /by YYYY-MM-DD [HHMM]",
        )

        if user_response_match is None:
            return

        description = user_response_match.group(1)
        parsed_deadline = self._parse_deadline(user_response_match.group(2))

        if parsed_deadline is None:
            return

        due_date, due_time = parsed_deadline

        task = Task(description, "deadline")
        task.due_date = due_date
        task.due_time = due_time

        self._append_task(task)

    def _add_event_task(self, user_response: str) -> None:
        """
        Creates and adds an event task from command text.
        Prints confirmation on success, or usage guidance for invalid input.

        Args:
        -----
        user_response (str): A command in the format
            "event <description> /from <start> /to <end>".

        Returns:
        --------
        None.
        """
        user_response_match = self._match_user_response(
            user_response,
            r"^event\s+(.+?)\s+/from\s+(.+?)\s+/to\s+(.+)$",
            "Use: event <description> /from <start> /to <end>",
        )

        if user_response_match is None:
            return

        description = user_response_match.group(1)
        start = user_response_match.group(2)
        end = user_response_match.group(3)

        task = Task(description, "event")
        task.start = start
        task.end = end

        self._append_task(task)

    def add_task(self, user_response: str) -> None:
        """
        Routes a task-creation command to the appropriate task handler.
        Prints usage guidance if the task type is unrecognized.

        Args:
        -----
        user_response (str): The full todo, deadline, event, or recurring command.

        Returns:
        --------
        None.
        """
        task_type = user_response.split(" ", 1)[0]

        if task_type == "todo":
            self._add_todo_task(user_response)

        elif task_type == "event":
            self._add_event_task(user_response)

        elif task_type == "deadline":
            self._add_deadline_task(user_response)

        elif task_type == "recurring":
            self._add_recurring_task(user_response)

        else:
            print(
                "Use:\n"
                "  todo <description>\n"
                "  deadline <description> /by YYYY-MM-DD [HHMM]\n"
                "  event <description> /from <start> /to <end>\n"
                "  recurring <description> /every <day>")

    def list_tasks(self) -> None:
        """
        Prints all tasks with numbering starting at 1,
        followed by the number of incomplete tasks.

        Returns:
        --------
        None.
        """
        for i, task in enumerate(self.tasks, start=1):
            print(f"{i}. {task}")
         
        undone_task_count = sum(1 for task in self.tasks if not task.done)
        print(f"That's {undone_task_count} on your plate.")

    def list_due_tasks(self, user_response: str) -> None:
        """
        Prints deadlines due on the requested date, numbered from 1.
        Includes completed tasks and ignores deadline times.
        Prints guidance for invalid input or a message if nothing matches.

        Args:
        -----
        user_response (str): A command in the format "due YYYY-MM-DD".

        Returns:
        --------
        None.
        """
        user_response_match = self._match_user_response(
            user_response,
            r"^due\s+([0-9]{4}-[0-9]{2}-[0-9]{2})$",
            "Use: due YYYY-MM-DD",
        )

        if user_response_match is None:
            return

        try:
            query_date = date.fromisoformat(user_response_match.group(1))
        except ValueError:
            print("Invalid date. Use a valid calendar date as YYYY-MM-DD.")
            return

        matching_tasks = [
            task for task in self.tasks
            if task.task_type == "deadline" and task.due_date == query_date
        ]

        if not matching_tasks:
            print(f"No deadlines due on {query_date}.")
            return

        for i, task in enumerate(matching_tasks, start=1):
            print(f"{i}. {task}")

    def mark_task(self, user_response: str) -> None:
        """
        Marks the specified task as complete, saves it, and prints confirmation.
        Prints guidance if the command or task number is invalid.

        Args:
        -----
        user_response (str): A command in the format "mark <number>",
            where number is the task's position in the list, starting at 1.

        Returns:
        --------
        None.
        """
        user_response_match = self._match_user_response(
            user_response,
            r"^mark\s+(\d+)$",
            "Use: mark <number>",
        )

        if user_response_match is None:
            return

        task_number = int(user_response_match.group(1))

        if not self._check_task_number(task_number):
            return

        task = self.tasks[task_number - 1]
        task.mark_done()
        self._save_tasks()
        print(f"Done:\n{task}")

    def unmark_task(self, user_response: str) -> None:
        """
        Marks the specified task as incomplete, saves it, and prints confirmation.
        Prints guidance if the command or task number is invalid.

        Args:
        -----
        user_response (str): A command in the format "unmark <number>",
            where number is the task's position in the list, starting at 1.

        Returns:
        --------
        None.
        """
        user_response_match = self._match_user_response(
            user_response,
            r"^unmark\s+(\d+)$",
            "Use: unmark <number>",
        )

        if user_response_match is None:
            return

        task_number = int(user_response_match.group(1))

        if not self._check_task_number(task_number):
            return

        task = self.tasks[task_number - 1]
        task.unmark_done()
        self._save_tasks()
        print(f"Not done:\n{task}")

    def note_task(self, user_response: str) -> None:
        """
        Stores a note on the specified task, replacing any existing note.
        Saves the updated task list.
        Prints confirmation, or guidance if the command or task number is invalid.

        Args:
        -----
        user_response (str): A command in the format "note <number> <note>",
            where number is the task's position in the list, starting at 1.

        Returns:
        --------
        None.
        """
        user_response_match = self._match_user_response(
            user_response,
            r"^note\s+(\d+)\s+(.+)$",
            "Use: note <number> <note>",
        )

        if user_response_match is None:
            return

        task_number = int(user_response_match.group(1))
        note = user_response_match.group(2)

        if not self._check_task_number(task_number):
            return

        task = self.tasks[task_number - 1]
        task.add_note(note)
        self._save_tasks()
        print(f"Noted:\n{task}")

    def delete_task(self, user_response: str) -> None:
        """
        Removes the specified task and prints it with the remaining task count.
        Saves the updated task list before printing confirmation.
        Prints guidance if the command or task number is invalid.

        Args:
        -----
        user_response (str): A command in the format "delete <number>",
            where number is the task's position in the list, starting at 1.

        Returns:
        --------
        None.
        """
        user_response_match = self._match_user_response(
            user_response,
            r"^delete\s+(\d+)$",
            "Use: delete <number>",
        )

        if user_response_match is None:
            return

        task_number = int(user_response_match.group(1))

        if not self._check_task_number(task_number):
            return

        task = self.tasks.pop(task_number - 1)
        self._save_tasks()
        print(f"Deleted:\n{task}")
        remaining = len(self.tasks)
        print(f"{remaining} tasks left.")

def chat() -> None:
    """
    Runs an interactive task-management session with the saved task collection.
    Reads terminal commands and dispatches task operations until "bye" is entered.
    Prints guidance for unrecognized commands. Successful changes are saved.

    Returns:
    --------
    None.
    """

    tasks = Tasks()

    while True:
        user_response = input("> ")

        if user_response == "bye":
            break

        elif user_response == "list":
            tasks.list_tasks()

        elif user_response.startswith("due"):
            tasks.list_due_tasks(user_response)

        elif user_response.startswith("mark"):
            tasks.mark_task(user_response)

        elif user_response.startswith("unmark"):
            tasks.unmark_task(user_response)

        elif user_response.startswith("note"):
            tasks.note_task(user_response)

        elif user_response.startswith("delete"):
            tasks.delete_task(user_response)
        
        elif user_response.startswith(("todo", "deadline", "event", "recurring")):
            tasks.add_task(user_response)
            
        else:
            print("Never heard of it. Try: todo, deadline, event, recurring, list, due, mark, unmark, note, delete, bye.")

def main() -> None:
    """
    Runs Bao's command-line interface.
    Prints the opening greeting, starts the chat session,
    and prints the closing message when the session ends normally.

    Returns:
    --------
    None.
    """
    greeting()
    try:
        chat()
    except (OSError, ValueError) as error:
        print(error)
        return
    farewell()
