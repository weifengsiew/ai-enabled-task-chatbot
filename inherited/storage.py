"""Load and save task data for the inherited Bao application."""

import json
from pathlib import Path
from typing import Any, cast


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


def load_tasks(data_file: Path) -> list[dict[str, Any]]:
    """Read task data from a JSON file.

    Args:
        data_file: Source file containing saved task data.

    Returns:
        The decoded task data, or an empty list if the file is absent.

    Raises:
        OSError: If the file cannot be read.
        json.JSONDecodeError: If the file contains invalid JSON.
    """
    if not data_file.exists():
        return []
    return cast(list[dict[str, Any]], json.loads(data_file.read_text()))
