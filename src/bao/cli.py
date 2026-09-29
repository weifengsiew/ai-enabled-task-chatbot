"""Command-line entry point for bao."""
import re

def greeting() -> None:
    """Greet the user."""
    print("Hello! I'm bao. What needs doing?")

def farewell() -> None:
    """End the conversation."""
    print("Later.")
    
class Task:
    def __init__(self, description: str, task_type: str) -> None:
        self.description = description
        self.done = False
        self.note = None
        self.task_type = task_type
        self.day = None

    def mark_done(self) -> None:
        """Mark the task as done."""
        self.done = True
    
    def unmark_done(self) -> None:
        """Mark the task as not done."""
        self.done = False

    def add_note(self, note: str) -> None:
        """Add a note to the task."""
        self.note = note

    def __str__(self) -> str:
        """Return a string representation of the task."""
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
        self.tasks: list[Task] = []

    def add_todo_task(self, user_response: str) -> None:
        """Add a todo task."""
        todo_pattern = r"^todo\s+(.+)$"
        match = re.fullmatch(todo_pattern, user_response)

        if not match:
            print("Use: todo <description>")
            return

        description = match.group(1)

        task = Task(description, "todo")
        self.tasks.append(task)

        print(f"Added:\n{task}")
    
    def add_recurring_task(self, user_response: str) -> None:
        """Add a recurring task."""
        recurring_pattern = r"^recurring\s+(.+?)\s+/every\s+(\w+)$"
        match = re.fullmatch(recurring_pattern, user_response)

        if not match:
            print("Use: recurring <description> /every <day>")
            return

        description = match.group(1)
        day = match.group(2)

        task = Task(description, "recurring")
        task.day = day

        self.tasks.append(task)
        print(f"Added:\n{task}")

    def add_deadline_task(self, user_response: str) -> None:
        """Add a deadline task."""
        deadline_pattern = r"^deadline\s+(.+?)\s+/by\s+(\w+)$"
        match = re.fullmatch(deadline_pattern, user_response)

        if not match:
            print("Use: deadline <description> /by <day>")
            return

        description = match.group(1)
        day = match.group(2)

        task = Task(description, "deadline")
        task.day = day

        self.tasks.append(task)
        print(f"Added:\n{task}")

    def add_event_task(self, user_response: str) -> None:
        """Add an event task."""
        event_pattern = r"^event\s+(.+?)\s+/from\s+(.+?)\s+/to\s+(.+)$"
        match = re.fullmatch(event_pattern, user_response)

        if not match:
            print("Use: event <description> /from <start> /to <end>")
            return

        description = match.group(1)
        start = match.group(2)
        end = match.group(3)

        task = Task(description, "event")
        task.start = start
        task.end = end

        self.tasks.append(task)
        print(f"Added:\n{task}")

    def add_task(self, user_response: str) -> None:
        """Add a new task to the list."""
        task_type = user_response.split(" ", 1)[0]

        if task_type == "todo":
            self.add_todo_task(user_response)

        elif task_type == "event":
            self.add_event_task(user_response)

        elif task_type == "deadline":
            self.add_deadline_task(user_response)

        elif task_type == "recurring":
            self.add_recurring_task(user_response)

        else:
            print(
                "Use:\n"
                "  todo <description>\n"
                "  deadline <description> /by <day>\n"
                "  event <description> /from <start> /to <end>\n"
                "  recurring <description> /every <day>")

    def list_tasks(self) -> None:
        """List all tasks."""
        for i, task in enumerate(self.tasks, start=1):
            print(f"{i}. {task}")
         
        undone_task_count = sum(1 for task in self.tasks if not task.done)
        print(f"That's {undone_task_count} on your plate.")

    def mark_task(self, user_response: str) -> None:
        """Mark a task as done."""
        mark_pattern = r"^mark\s+(\d+)$"
        match = re.fullmatch(mark_pattern, user_response)

        if not match:
            print("Use: mark <number>")
            return

        task_number = int(match.group(1))

        if 1 <= task_number <= len(self.tasks):
            self.tasks[task_number - 1].mark_done()
            print("Done:")
            print(self.tasks[task_number - 1])
        else:
            if self.tasks:
                invalid_task_number_message = f"Choose a number from 1 to {len(self.tasks)}."
            else:
                invalid_task_number_message = "There are no tasks yet."
            print(f"No task {task_number}. {invalid_task_number_message}")

    def unmark_task(self, user_response: str) -> None:
        """Mark a task as not done."""
        unmark_pattern = r"^unmark\s+(\d+)$"
        match = re.fullmatch(unmark_pattern, user_response)

        if not match:
            print("Use: unmark <number>")
            return

        task_number = int(match.group(1))

        if 1 <= task_number <= len(self.tasks):
            self.tasks[task_number - 1].unmark_done()
            print("Not done:")
            print(self.tasks[task_number - 1])
        else:
            if self.tasks:
                invalid_task_number_message = f"Choose a number from 1 to {len(self.tasks)}."
            else:
                invalid_task_number_message = "There are no tasks yet."
            print(f"No task {task_number}. {invalid_task_number_message}")

    def note_task(self, user_response: str) -> None:
        """Add a note to a task."""
        note_pattern = r"^note\s+(\d+)\s+(.+)$"
        match = re.fullmatch(note_pattern, user_response)

        if not match:
            print("Use: note <number> <note>")
            return

        task_number = int(match.group(1))
        note = match.group(2)

        if 1 <= task_number <= len(self.tasks):
            self.tasks[task_number - 1].add_note(note)
            print("Noted:")
            print(self.tasks[task_number - 1])
        else:
            if self.tasks:
                invalid_task_number_message = f"Choose a number from 1 to {len(self.tasks)}."
            else:
                invalid_task_number_message = "There are no tasks yet."
            print(f"No task {task_number}. {invalid_task_number_message}")

def chat() -> None:
    """Chat with the user."""

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
        
        elif user_response.startswith(("todo", "deadline", "event", "recurring")):
            tasks.add_task(user_response)
            
        else:
            print("Never heard of it. Try: todo, deadline, event, recurring, list, mark, unmark, note, bye.")

def main() -> None:
    """Run bao."""
    greeting()
    chat()
    farewell()
