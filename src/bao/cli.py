"""Command-line entry point for bao."""


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


def chat() -> None:
    """Chat with the user."""

    tasks: list[Task] = []

    while True:
        user_response = input("> ")

        if user_response == "bye":
            break

        elif user_response == "list":
            for i, task in enumerate(tasks, start=1):
                print(f"{i}. {task}")

        elif user_response.startswith("mark "):
            parts = user_response.split()

            if len(parts) == 2 and parts[1].isdigit():
                task_number = int(parts[1])

                if 1 <= task_number <= len(tasks):
                    tasks[task_number - 1].mark_done()
                    print("Done:")
                    print(tasks[task_number - 1])
                else:
                    print("Task does not exist.")
            else:
                print("Use: mark <number>")

        elif user_response.startswith("unmark "):
            parts = user_response.split()

            if len(parts) == 2 and parts[1].isdigit():
                task_number = int(parts[1])

                if 1 <= task_number <= len(tasks):
                    tasks[task_number - 1].unmark_done()
                    print("Not done:")
                    print(tasks[task_number - 1])
                else:
                    print("Task does not exist.")
            else:
                print("Use: mark <number>")
        
        elif user_response.startswith("note "):
            parts = user_response.split(" ", 2)

            if len(parts) == 3 and parts[1].isdigit():
                task_number = int(parts[1])
                note = parts[2]

                if 1 <= task_number <= len(tasks):
                    tasks[task_number - 1].add_note(note)
                    print("Noted:")
                    print(tasks[task_number - 1])
                else:
                    print("Task does not exist.")
            else:
                print("Use: note <number> <note>")

        else:
            task = Task(user_response)
            tasks.append(task)
            print(f"Added: {user_response}")

def main() -> None:
    """Run bao."""
    print("Hello! I'm bao. What needs doing?")
    chat()
    farewell()
