# Command class specification

This specification describes the proposed `Command` base class and the
`CommandToDo` child class. Other command classes should follow the same pattern
after this design is accepted and implemented.

## `Command`

`Command` is the common abstraction for a validated user command. It owns the
interface and behavior shared by command types, while each child owns the
syntax, data, validation, execution, and response behavior specific to its
command.

The command lifecycle is:

```text
user response
    -> parse and validate
    -> create a command instance, or return guidance
    -> execute the command
    -> return the success message
```

The base class should define the common command protocol. It should not own the
interactive input loop, task collection, JSON persistence, or direct terminal
input and output.

```python
from abc import ABC, abstractmethod
from typing import ClassVar


class Command(ABC):
    """Common interface for validated user commands."""

    command_keyword: ClassVar[str]
    command_pattern: ClassVar[re.Pattern[str]]
    command_usage: ClassVar[str]

    @classmethod
    @abstractmethod
    def parse(cls, user_response: str) -> Command | str | None:
        """Parse this command's input, if the input belongs to this command."""

    @abstractmethod
    def execute(self, tasks: Tasks) -> str:
        """Execute the command and return its success message."""
```

`parse()` returns `None` when the input belongs to another command. If the
input appears to belong to the command but is invalid, it returns a guidance
string. Valid input produces a concrete command instance. `execute()` is called
only on a valid command instance and returns a message for the caller to
display.

## `CommandToDo`

`CommandToDo` represents the `todo <description>` command. It should contain as
many to-do-specific details as possible.

### Stored attributes

`CommandToDo` initializes its command configuration on each instance:

```python
class CommandToDo(Command):
    def __init__(self, task_description: str) -> None:
        self.command_keyword = "todo"
        self.command_usage = "todo <description>"
        self.command_pattern = re.compile(r"^todo\s+(.+)$")
        self.guidance_message = "Use: todo <description>"
        self.success_prefix = "Added:"
        self.minimum_description_length = 1
        self.maximum_description_length = 500
        self.task_description = task_description
```

The instance stores both its command configuration and the data for one parsed
to-do command. It does not permanently store the raw user response, the
`Tasks` service, the created task, the task list, or the JSON file path.

### Proposed implementation shape

```python
import re


class CommandToDo(Command):
    """Parse and execute a to-do command."""

    def __init__(self, task_description: str) -> None:
        self.command_keyword = "todo"
        self.command_usage = "todo <description>"
        self.command_pattern = re.compile(r"^todo\s+(.+)$")
        self.guidance_message = "Use: todo <description>"
        self.success_prefix = "Added:"
        self.minimum_description_length = 1
        self.maximum_description_length = 500
        self.task_description = task_description

    @classmethod
    def parse(cls, user_response: str) -> CommandToDo | str | None:
        """Recognize, parse, and validate a to-do response."""
        command = cls("")
        if user_response != command.command_keyword and not user_response.startswith(
            f"{command.command_keyword} "
        ):
            return None

        match = command.command_pattern.fullmatch(user_response)
        if match is None:
            return command.guidance_message

        task_description = match.group(1).strip()
        if not task_description:
            return command.guidance_message

        return cls(task_description)

    def execute(self, tasks: Tasks) -> str:
        """Create the to-do task and return its success message."""
        task = tasks.add_todo(self.task_description)
        return f"{self.success_prefix}\n{task}"
```

### Example behavior

```python
CommandToDo.parse("list")
# None

CommandToDo.parse("todo")
# "Use: todo <description>"

command = CommandToDo.parse("todo read paper")
# CommandToDo(description="read paper")

message = command.execute(tasks)
# "Added:\n[T][ ]read paper"
```

The command returns messages rather than calling `print()`. The conversation
loop remains responsible for displaying the returned message.

## Strong ownership for `CommandToDo`

`CommandToDo` should own the complete meaning and behavior of the `todo`
command. It should be the single place that defines how a to-do command is
recognized, interpreted, validated, converted into a task, executed, and
reported.

### Additional attributes and methods

```python
class CommandToDo(Command):
    def __init__(self, task_description: str) -> None:
        self.command_keyword = "todo"
        self.aliases = ()
        self.command_usage = "todo <description>"
        self.command_pattern = re.compile(r"^todo\s+(.+)$")
        self.guidance_message = "Use: todo <description>"
        self.success_prefix = "Added:"
        self.minimum_description_length = 1
        self.maximum_description_length = 500
        self.task_description = task_description
```

The instance attributes define the command's syntax, constraints, user-facing
messages, and parsed description. This keeps the complete to-do command
configuration together on the command instance.

### Additional methods

```python
class CommandToDo(Command):
    @classmethod
    def matches(cls, user_response: str) -> bool:
        """Return whether the input appears to be a to-do command."""

    @classmethod
    def normalize_task_description(cls, task_description: str) -> str:
        """Normalize whitespace and other to-do-specific input."""

    @classmethod
    def validate_task_description(cls, task_description: str) -> str | None:
        """Validate the normalized to-do description."""

    def create_task(self) -> TodoTask:
        """Build a TodoTask from this command's validated description."""

    def execute(self, tasks: Tasks) -> str:
        """Create and save the to-do task and return its success message."""

    def success_message(self, task: TodoTask) -> str:
        """Format the successful to-do response."""

    @classmethod
    def help_message(cls) -> str:
        """Return the usage guidance for the to-do command."""
```

The complete internal flow should be:

```text
parse()
    -> matches()
    -> extract description
    -> normalize_task_description()
    -> validate_task_description()
    -> create CommandToDo

execute()
    -> create_task()
    -> Tasks.add_todo()
    -> success_message()
    -> return message
```

This gives `CommandToDo` strong ownership without making it responsible for
application-wide concerns. It should not read from `input()`, call `print()`,
manage the complete task collection, or write JSON directly. The conversation
loop displays the returned guidance or success message, `Tasks` manages the
collection and persistence workflow, and the command owns everything specific
to the `todo` meaning and behavior.
