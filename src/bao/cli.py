"""Command-line entry point for bao."""

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
        self.recurring_day = None

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
        recurring_day = f" (every: {self.recurring_day})" if self.recurring_day else ""

        return f"{task_type_mark}{done_mark}{self.description}" + (
            f"\n{note}" if note else "") + recurring_day

class Tasks:
    def __init__(self) -> None:
        self.tasks: list[Task] = []

    def add_task(self, user_response: str) -> None:
        """Add a new task to the list."""
        parts = user_response.split(" ", 1)

        if len(parts) == 2:
            task_type = parts[0]
            description = parts[1]
        
            if task_type in ["todo", "deadline", "event"]:
                task = Task(description, task_type)
                self.tasks.append(task)
                print(f"Added:\n{task}")

            elif task_type == "recurring":
                left, day = user_response.split(" /every ", 1)
                task_type, description = left.split(" ", 1)
                parts = [task_type, description, "/every", day]
                task = Task(description, task_type)
                task.recurring_day = day
                self.tasks.append(task)
                print(f"Added:\n{task}")

            else:
                print(
                "Use:\n"
                "  todo <description>\n"
                "  deadline <description>\n"
                "  event <description>"
                )
        else:
            print(
                "Use:\n"
                "  todo <description>\n"
                "  deadline <description>\n"
                "  event <description>\n"
                "  recurring <description>"
            )

    def list_tasks(self) -> None:
        """List all tasks."""
        for i, task in enumerate(self.tasks, start=1):
            print(f"{i}. {task}")
         
        undone_task_count = sum(1 for task in self.tasks if not task.done)
        print(f"That's {undone_task_count} on your plate.")

    def mark_task(self, user_response: str) -> None:
        """Mark a task as done."""
        parts = user_response.split()

        if len(parts) == 2 and parts[1].isdigit():
            task_number = int(parts[1])

            if 1 <= task_number <= len(self.tasks):
                self.tasks[task_number - 1].mark_done()
                print("Done:")
                print(self.tasks[task_number - 1])
            else:
                print("Task does not exist.")
        else:
            print("Use: mark <number>")

    def unmark_task(self, user_response: str) -> None:
        """Mark a task as not done."""
        parts = user_response.split()

        if len(parts) == 2 and parts[1].isdigit():
            task_number = int(parts[1])

            if 1 <= task_number <= len(self.tasks):
                self.tasks[task_number - 1].unmark_done()
                print("Not done:")
                print(self.tasks[task_number - 1])
            else:
                print("Task does not exist.")
        else:
            print("Use: unmark <number>")

    def note_task(self, user_response: str) -> None:
        """Add a note to a task."""
        parts = user_response.split(" ", 2)

        if len(parts) == 3 and parts[1].isdigit():
            task_number = int(parts[1])
            note = parts[2]

            if 1 <= task_number <= len(self.tasks):
                self.tasks[task_number - 1].add_note(note)
                print("Noted:")
                print(self.tasks[task_number - 1])
            else:
                print("Task does not exist.")
        else:
            print("Use: note <number> <note>")
    

def chat() -> None:
    """Chat with the user."""

    tasks = Tasks()

    while True:
        user_response = input("> ")

        if user_response == "bye":
            break

        elif user_response == "list":
            tasks.list_tasks()

        elif user_response.startswith("mark "):
            tasks.mark_task(user_response)

        elif user_response.startswith("unmark "):
            tasks.unmark_task(user_response)

        elif user_response.startswith("note "):
            tasks.note_task(user_response)
        
        elif user_response.startswith(("todo ", "deadline ", "event ", "recurring")):
            tasks.add_task(user_response)
            
        else:
            print("I don't understand that command.")

def main() -> None:
    """Run bao."""
    greeting()
    chat()
    farewell()
