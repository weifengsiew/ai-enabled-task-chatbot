"""Working but deliberately tangled code for the Stage R refactoring exercise."""

import json
from datetime import datetime
from pathlib import Path


TASKS = []
DATA_FILE = Path("data/inherited-tasks.json")


def run():
    TASKS.clear()
    if DATA_FILE.exists():
        try:
            TASKS.extend(json.loads(DATA_FILE.read_text()))
        except (OSError, json.JSONDecodeError):
            print("Could not read saved tasks. Starting with an empty list.")

    print("bao here. What needs doing?")
    while True:
        try:
            line = input("> ")
        except (EOFError, KeyboardInterrupt):
            print("Later.")
            return

        if not line.strip():
            print("Nothing there.")
        elif line == "bye":
            print("Later.")
            return
        elif line == "list":
            if not TASKS:
                print("Nothing on your plate.")
            else:
                for number, task in enumerate(TASKS, 1):
                    box = "X" if task["done"] else " "
                    if task["kind"] == "todo":
                        display = f'[T][{box}] {task["description"]}'
                    elif task["kind"] == "deadline":
                        due = datetime.fromisoformat(task["when"])
                        if due.hour == 0 and due.minute == 0:
                            formatted = due.strftime("%b %d %Y")
                        else:
                            formatted = due.strftime("%b %d %Y, ") + due.strftime("%I%p").lstrip(
                                "0"
                            ).lower()
                        display = f'[D][{box}] {task["description"]} (by: {formatted})'
                    elif task["kind"] == "event":
                        display = (
                            f'[E][{box}] {task["description"]} '
                            f'(from: {task["from"]} to: {task["to"]})'
                        )
                    else:
                        display = f'[R][{box}] {task["description"]} (every: {task["every"]})'
                    print(f"{number}.{display}")
                    if task["note"]:
                        print(f'   Note: {task["note"]}')
        elif line.startswith("todo "):
            description = line[5:].strip()
            if not description:
                print("A to-do needs something to do.")
                continue
            task = {"kind": "todo", "description": description, "done": False, "note": ""}
            TASKS.append(task)
            print("Added:")
            print(f"  [T][ ] {description}")
            DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
            DATA_FILE.write_text(json.dumps(TASKS, indent=2))
        elif line.startswith("deadline"):
            rest = line[len("deadline") :].strip()
            if "/by" not in rest:
                print("A deadline needs something to do and a /by.")
                continue
            description, when_text = (part.strip() for part in rest.split("/by", 1))
            if not description or not when_text:
                print("A deadline needs something to do and a /by.")
                continue
            parsed = None
            for pattern in ("%Y-%m-%d %H%M", "%Y-%m-%d"):
                try:
                    parsed = datetime.strptime(when_text, pattern)
                    break
                except ValueError:
                    pass
            if parsed is None:
                print("Use YYYY-MM-DD with an optional four-digit time.")
                continue
            task = {
                "kind": "deadline",
                "description": description,
                "done": False,
                "note": "",
                "when": parsed.isoformat(),
            }
            TASKS.append(task)
            if parsed.hour == 0 and parsed.minute == 0:
                formatted = parsed.strftime("%b %d %Y")
            else:
                formatted = parsed.strftime("%b %d %Y, ") + parsed.strftime("%I%p").lstrip(
                    "0"
                ).lower()
            print("Added:")
            print(f"  [D][ ] {description} (by: {formatted})")
            DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
            DATA_FILE.write_text(json.dumps(TASKS, indent=2))
        elif line.startswith("event"):
            rest = line[len("event") :].strip()
            if "/from" not in rest or "/to" not in rest:
                print("An event needs a description, /from, and /to.")
                continue
            description, times = (part.strip() for part in rest.split("/from", 1))
            start, end = (part.strip() for part in times.split("/to", 1))
            if not description or not start or not end:
                print("An event needs a description, /from, and /to.")
                continue
            task = {
                "kind": "event",
                "description": description,
                "done": False,
                "note": "",
                "from": start,
                "to": end,
            }
            TASKS.append(task)
            print("Added:")
            print(f"  [E][ ] {description} (from: {start} to: {end})")
            DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
            DATA_FILE.write_text(json.dumps(TASKS, indent=2))
        elif line.startswith("recurring"):
            rest = line[len("recurring") :].strip()
            if "/every" not in rest:
                print("A recurring task needs something to do and an /every.")
                continue
            description, every = (part.strip() for part in rest.split("/every", 1))
            if not description or not every:
                print("A recurring task needs something to do and an /every.")
                continue
            task = {
                "kind": "recurring",
                "description": description,
                "done": False,
                "note": "",
                "every": every,
            }
            TASKS.append(task)
            print("Added:")
            print(f"  [R][ ] {description} (every: {every})")
            DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
            DATA_FILE.write_text(json.dumps(TASKS, indent=2))
        elif line.startswith("mark") or line.startswith("unmark"):
            pieces = line.split()
            command = pieces[0]
            if len(pieces) != 2:
                print(f"Tell me which task to {command}, for example: {command} 2.")
                continue
            try:
                index = int(pieces[1]) - 1
            except ValueError:
                print("The task number must be a whole number.")
                continue
            if index < 0 or index >= len(TASKS):
                print(f"No task {pieces[1]}.")
                continue
            TASKS[index]["done"] = command == "mark"
            box = "X" if TASKS[index]["done"] else " "
            print("Done:" if command == "mark" else "Not done:")
            print(f'  [{box}] {TASKS[index]["description"]}')
            DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
            DATA_FILE.write_text(json.dumps(TASKS, indent=2))
        elif line.startswith("note"):
            pieces = line.split(maxsplit=2)
            if len(pieces) != 3:
                print("Use note NUMBER TEXT, for example: note 2 ask about funding.")
                continue
            try:
                index = int(pieces[1]) - 1
            except ValueError:
                print("The task number must be a whole number.")
                continue
            if index < 0 or index >= len(TASKS):
                print(f"No task {pieces[1]}.")
                continue
            TASKS[index]["note"] = pieces[2]
            print("Noted:")
            print(f'  {TASKS[index]["description"]}')
            print(f"  Note: {pieces[2]}")
            DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
            DATA_FILE.write_text(json.dumps(TASKS, indent=2))
        elif line.startswith("delete"):
            pieces = line.split()
            if len(pieces) != 2:
                print("Tell me which task to delete, for example: delete 2.")
                continue
            try:
                index = int(pieces[1]) - 1
            except ValueError:
                print("The task number must be a whole number.")
                continue
            if index < 0 or index >= len(TASKS):
                print(f"No task {pieces[1]}.")
                continue
            removed = TASKS.pop(index)
            print("Deleted:")
            print(f'  {removed["description"]}')
            print(f"{len(TASKS)} tasks left.")
            DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
            DATA_FILE.write_text(json.dumps(TASKS, indent=2))
        elif line == "clear":
            before = len(TASKS)
            TASKS[:] = [task for task in TASKS if not task["done"]]
            removed = before - len(TASKS)
            print(f"Cleared {removed} completed tasks.")
            print(f"{len(TASKS)} tasks left.")
            DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
            DATA_FILE.write_text(json.dumps(TASKS, indent=2))
        elif line.startswith("find"):
            query = line[len("find") :].strip()
            if not query:
                print("Tell me what to find.")
                continue
            matches = [task for task in TASKS if query.casefold() in task["description"].casefold()]
            if not matches:
                print("No matching tasks.")
            for number, task in enumerate(matches, 1):
                box = "X" if task["done"] else " "
                print(f'{number}.[{box}] {task["description"]}')
        elif line.startswith("due"):
            date_text = line[len("due") :].strip()
            try:
                wanted = datetime.strptime(date_text, "%Y-%m-%d").date()
            except ValueError:
                print("Use due YYYY-MM-DD.")
                continue
            matches = [
                task
                for task in TASKS
                if task["kind"] == "deadline"
                and datetime.fromisoformat(task["when"]).date() == wanted
            ]
            if not matches:
                print("Nothing due that day.")
            for number, task in enumerate(matches, 1):
                due = datetime.fromisoformat(task["when"])
                if due.hour == 0 and due.minute == 0:
                    formatted = due.strftime("%b %d %Y")
                else:
                    formatted = due.strftime("%b %d %Y, ") + due.strftime("%I%p").lstrip(
                        "0"
                    ).lower()
                box = "X" if task["done"] else " "
                print(f'{number}.[D][{box}] {task["description"]} (by: {formatted})')
        else:
            print(
                "Never heard of it. Try: todo, deadline, event, recurring, list, mark, "
                "unmark, note, delete, clear, find, due, bye."
            )


if __name__ == "__main__":
    run()
