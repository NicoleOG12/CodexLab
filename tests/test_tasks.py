from __future__ import annotations

import json
from pathlib import Path

from app import service
from app.store import load_tasks


def _write_tasks(tmp_path: Path, tasks: list[dict]) -> Path:
    data_path = tmp_path / "tasks.json"
    data_path.write_text(json.dumps(tasks), encoding="utf-8")
    return data_path


def test_status_filter_and_search_work(tmp_path):
    data_path = _write_tasks(
        tmp_path,
        [
            {
                "id": 1,
                "title": "Write launch recap",
                "description": "Draft a short internal summary of the product launch.",
                "status": "open",
                "priority": "high",
                "created_at": "2026-02-25T16:00:00+00:00",
                "completed_at": None,
            },
            {
                "id": 2,
                "title": "Fix login redirect",
                "description": "Resolve the redirect loop after the OAuth callback.",
                "status": "done",
                "priority": "high",
                "created_at": "2026-02-20T14:30:00+00:00",
                "completed_at": "2026-02-21T09:15:00+00:00",
            },
            {
                "id": 3,
                "title": "Plan workshop agenda",
                "description": "Outline topics for the partner onboarding session.",
                "status": "open",
                "priority": "medium",
                "created_at": "2026-02-27T11:45:00+00:00",
                "completed_at": None,
            },
        ],
    )

    import app.store as store

    store.DATA_FILE = data_path

    assert [task["id"] for task in service.list_tasks(status="open")] == [1, 3]
    assert [task["id"] for task in service.list_tasks(q="launch")] == [1]
    assert [task["id"] for task in service.list_tasks(status="open", q="plan")] == [3]


def test_complete_task_persists_changes(tmp_path):
    data_path = _write_tasks(
        tmp_path,
        [
            {
                "id": 1,
                "title": "Write launch recap",
                "description": "Draft a short internal summary of the product launch.",
                "status": "open",
                "priority": "high",
                "created_at": "2026-02-25T16:00:00+00:00",
                "completed_at": None,
            }
        ],
    )

    import app.store as store

    store.DATA_FILE = data_path

    result = service.complete_task(1)

    assert result is not None
    assert result["status"] == "done"
    assert result["completed_at"] is not None
    stored = load_tasks()
    assert stored[0]["status"] == "done"
    assert stored[0]["completed_at"] is not None
