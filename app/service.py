from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .store import load_tasks, next_task_id, save_tasks


def list_tasks(status: str | None = None, q: str | None = None) -> list[dict[str, Any]]:
    """Return task records, optionally filtered by status and search text."""
    tasks = load_tasks()
    filtered: list[dict[str, Any]] = []

    for task in tasks:
        # Filter by status
        if status and task["status"] != status:
            continue

        # Filter by search query (case-insensitive match against title and description)
        if q and q.lower() not in task["title"].lower() and q.lower() not in task["description"].lower():
            continue

        filtered.append(task)

    return filtered


def get_task(task_id: int) -> dict[str, Any] | None:
    """Find a single task by ID."""
    tasks = load_tasks()
    return next((task for task in tasks if task["id"] == task_id), None)


def create_task(payload: dict[str, Any]) -> dict[str, Any]:
    """Create a new task and persist it."""
    tasks = load_tasks()
    task = {
        "id": next_task_id(tasks),
        "title": payload["title"],
        "description": payload["description"],
        "status": "open",
        "priority": payload["priority"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": None,
    }
    tasks.append(task)
    save_tasks(tasks)
    return task


def complete_task(task_id: int) -> dict[str, Any] | None:
    """Mark a task as completed."""
    tasks = load_tasks()

    for i, task in enumerate(tasks):
        if task["id"] == task_id:
            updated_task = dict(task)
            updated_task["status"] = "done"
            updated_task["completed_at"] = datetime.now(timezone.utc).isoformat()

            tasks[i] = updated_task  # Fix: Update the task in the list
            save_tasks(tasks)  # Fix: Persist the updated list
            return updated_task

    return None
