"""Command-line entry point for bao."""

def greeting() -> None:
    """Greet the user."""
    print("Hello! I'm bao. What needs doing?")

def farewell() -> None:
    """End the conversation."""
    print("Later.")
    
class Task:
    def __init__(self, description: str) -> None:
        self.description = description
        self.done = False
        self.note = None

    def mark_done(self) -> None:
        self.done = True
    
    def unmark_done(self) -> None:
        self.done = False

    def add_note(self, note: str) -> None:
        self.note = note

    def __str__(self) -> str:
        mark = "X" if self.done else " "
        note = f"Note: {self.note}" if self.note else None
        return f"[{mark}] {self.description}" + (f"\n{note}" if note is not None else "")


class Tasks:
    def __init__(self) -> None:
        self.tasks: list[Task] = []

    def add_task(self, description: str) -> None:
        self.tasks.append(Task(description))

    def list_tasks(self) -> None:
        for i, task in enumerate(self.tasks, start=1):
            print(f"{i}. {task}")

    def mark_task(self, user_response: str) -> None:
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

        else:
            task = Task(user_response)
            tasks.add_task(user_response)
            print(f"Added: {user_response}")

def main() -> None:
    """Run bao."""
    greeting()
    chat()
    farewell()
