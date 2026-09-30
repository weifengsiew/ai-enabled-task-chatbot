"""Save task data for the inherited Bao application."""

import json
from pathlib import Path
from typing import Any


def save_tasks(tasks: list[dict[str, Any]], data_file: Path) -> None:
    """Save tasks as JSON, creating the destination directory if needed.

    Args:
        tasks: Current task list to serialize without modifying it.
        data_file: Destination file to create or overwrite with task data.

    Returns:
        None.
    """
    data_file.parent.mkdir(parents=True, exist_ok=True)
    data_file.write_text(json.dumps(tasks, indent=2))
