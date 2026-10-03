"""Task models and conversion to the existing dictionary representation."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, ClassVar


@dataclass(kw_only=True)
class Task:
    """Shared description, completion state, and note for concrete task kinds.

    Subclasses supply their fixed kind and any additional fields.
    """

    description: str
    done: bool = False
    note: str = ""
    kind: ClassVar[str]

    def to_dict(self) -> dict[str, Any]:
        """Return a new dictionary containing this task's shared fields.

        Returns:
            Task data in the existing key order, without changing this object.
        """
        return {
            "kind": self.kind,
            "description": self.description,
            "done": self.done,
            "note": self.note,
        }


@dataclass(kw_only=True)
class TodoTask(Task):
    """A to-do task using the shared fields and defaults."""

    kind: ClassVar[str] = "todo"


@dataclass(kw_only=True)
class DeadlineTask(Task):
    """A task with a parsed deadline datetime."""

    when: datetime
    kind: ClassVar[str] = "deadline"

    def to_dict(self) -> dict[str, Any]:
        """Return task data with the deadline converted to the existing ISO text.

        Returns:
            A new dictionary containing shared fields followed by when.
        """
        task = super().to_dict()
        task["when"] = self.when.isoformat()
        return task


@dataclass(kw_only=True)
class EventTask(Task):
    """A task with start and end values stored as text."""

    start: str
    end: str
    kind: ClassVar[str] = "event"

    def to_dict(self) -> dict[str, Any]:
        """Return task data with start and end mapped to the existing keys.

        Returns:
            A new dictionary containing shared fields followed by from and to.
        """
        task = super().to_dict()
        task["from"] = self.start
        task["to"] = self.end
        return task


@dataclass(kw_only=True)
class RecurringTask(Task):
    """A task with a recurrence interval stored as text."""

    every: str
    kind: ClassVar[str] = "recurring"

    def to_dict(self) -> dict[str, Any]:
        """Return task data with the recurrence interval in the existing format.

        Returns:
            A new dictionary containing shared fields followed by every.
        """
        task = super().to_dict()
        task["every"] = self.every
        return task
