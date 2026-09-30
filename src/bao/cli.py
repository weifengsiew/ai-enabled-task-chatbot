"""Command-line entry point for bao."""
import re

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
        Initializes an incomplete task with no note or day assigned.

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
        task_type_marks = {
            "todo": "[T]",
            "deadline": "[D]",
            "event": "[E]",
            "recurring": "[R]"}
        task_type_mark = task_type_marks.get(self.task_type, "")
        done_mark = "[X]" if self.done else "[ ]"
        note = f"Note: {self.note}" if self.note else ""

        time_info = ""
        if self.task_type == "recurring" and self.day:
            time_info = f" (every: {self.day})"
        elif self.task_type == "deadline" and self.day:
            time_info = f" (by: {self.day})"
        elif self.task_type == "event" and self.start and self.end:
            time_info = f" (from: {self.start} to: {self.end})"

        return f"{task_type_mark}{done_mark}{self.description}" + time_info + (
            f"\n{note}" if note else "") 

class Tasks:
    def __init__(self) -> None:
        """
        Initializes an empty task collection.

        Returns:
        --------
        None.
        """
        self.tasks: list[Task] = []

    @staticmethod
    def _match_command(
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
        match = re.fullmatch(pattern, user_response)
        if match is None:
            print(usage)
        return match

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
        Appends a task to the collection and prints confirmation.

        Args:
        -----
        task (Task): The task to add to the collection.

        Returns:
        --------
        None.
        """
        self.tasks.append(task)
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
        match = self._match_command(
            user_response,
            r"^todo\s+(.+)$",
            "Use: todo <description>",
        )

        if match is None:
            return

        description = match.group(1)

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
        match = self._match_command(
            user_response,
            r"^recurring\s+(.+?)\s+/every\s+(\w+)$",
            "Use: recurring <description> /every <day>",
        )

        if match is None:
            return

        description = match.group(1)
        day = match.group(2)

        task = Task(description, "recurring")
        task.day = day

        self._append_task(task)

    def _add_deadline_task(self, user_response: str) -> None:
        """
        Creates and adds a deadline task from command text.
        Prints confirmation on success, or usage guidance for invalid input.

        Args:
        -----
        user_response (str): A command in the format
            "deadline <description> /by <day>".

        Returns:
        --------
        None.
        """
        match = self._match_command(
            user_response,
            r"^deadline\s+(.+?)\s+/by\s+(\w+)$",
            "Use: deadline <description> /by <day>",
        )

        if match is None:
            return

        description = match.group(1)
        day = match.group(2)

        task = Task(description, "deadline")
        task.day = day

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
        match = self._match_command(
            user_response,
            r"^event\s+(.+?)\s+/from\s+(.+?)\s+/to\s+(.+)$",
            "Use: event <description> /from <start> /to <end>",
        )

        if match is None:
            return

        description = match.group(1)
        start = match.group(2)
        end = match.group(3)

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
                "  deadline <description> /by <day>\n"
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

    def mark_task(self, user_response: str) -> None:
        """
        Marks the specified task as complete and prints confirmation.
        Prints guidance if the command or task number is invalid.

        Args:
        -----
        user_response (str): A command in the format "mark <number>",
            where number is the task's position in the list, starting at 1.

        Returns:
        --------
        None.
        """
        match = self._match_command(
            user_response,
            r"^mark\s+(\d+)$",
            "Use: mark <number>",
        )

        if match is None:
            return

        task_number = int(match.group(1))

        if not self._check_task_number(task_number):
            return

        task = self.tasks[task_number - 1]
        task.mark_done()
        print(f"Done:\n{task}")

    def unmark_task(self, user_response: str) -> None:
        """
        Marks the specified task as incomplete and prints confirmation.
        Prints guidance if the command or task number is invalid.

        Args:
        -----
        user_response (str): A command in the format "unmark <number>",
            where number is the task's position in the list, starting at 1.

        Returns:
        --------
        None.
        """
        match = self._match_command(
            user_response,
            r"^unmark\s+(\d+)$",
            "Use: unmark <number>",
        )

        if match is None:
            return

        task_number = int(match.group(1))

        if not self._check_task_number(task_number):
            return

        task = self.tasks[task_number - 1]
        task.unmark_done()
        print(f"Not done:\n{task}")

    def note_task(self, user_response: str) -> None:
        """
        Stores a note on the specified task, replacing any existing note.
        Prints confirmation, or guidance if the command or task number is invalid.

        Args:
        -----
        user_response (str): A command in the format "note <number> <note>",
            where number is the task's position in the list, starting at 1.

        Returns:
        --------
        None.
        """
        match = self._match_command(
            user_response,
            r"^note\s+(\d+)\s+(.+)$",
            "Use: note <number> <note>",
        )

        if match is None:
            return

        task_number = int(match.group(1))
        note = match.group(2)

        if not self._check_task_number(task_number):
            return

        task = self.tasks[task_number - 1]
        task.add_note(note)
        print(f"Noted:\n{task}")

    def delete_task(self, user_response: str) -> None:
        """
        Removes the specified task and prints it with the remaining task count.
        Prints guidance if the command or task number is invalid.

        Args:
        -----
        user_response (str): A command in the format "delete <number>",
            where number is the task's position in the list, starting at 1.

        Returns:
        --------
        None.
        """
        match = self._match_command(
            user_response,
            r"^delete\s+(\d+)$",
            "Use: delete <number>",
        )

        if match is None:
            return

        task_number = int(match.group(1))

        if not self._check_task_number(task_number):
            return

        task = self.tasks.pop(task_number - 1)
        print(f"Deleted:\n{task}")
        remaining = len(self.tasks)
        label = "task" if remaining == 1 else "tasks"
        print(f"{remaining} {label} left.")

def chat() -> None:
    """
    Runs an interactive task-management session with an empty task collection.
    Reads terminal commands and dispatches task operations until "bye" is entered.
    Prints guidance for unrecognized commands. Tasks are kept only for this session.

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
            print("Never heard of it. Try: todo, deadline, event, recurring, list, mark, unmark, note, delete, bye.")

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
    chat()
    farewell()
