import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app import service, store


class TaskServiceTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.data_path = Path(self.tempdir.name) / "tasks.json"
        self.data_path.write_text(
            json.dumps(
                [
                    {
                        "id": 1,
                        "title": "Write launch recap",
                        "description": "Draft a short internal summary of the product launch.",
                        "status": "open",
                        "priority": "high",
                        "created_at": "2026-02-25T16:00:00Z",
                        "completed_at": None,
                    },
                    {
                        "id": 2,
                        "title": "Fix login redirect",
                        "description": "Resolve the redirect loop after the OAuth callback.",
                        "status": "done",
                        "priority": "high",
                        "created_at": "2026-02-20T14:30:00Z",
                        "completed_at": "2026-02-21T09:15:00Z",
                    },
                    {
                        "id": 3,
                        "title": "Plan workshop agenda",
                        "description": "Outline topics for the partner onboarding session.",
                        "status": "open",
                        "priority": "medium",
                        "created_at": "2026-02-27T11:45:00Z",
                        "completed_at": None,
                    },
                ]
            ),
            encoding="utf-8",
        )
        self.patcher = patch.object(store, "DATA_FILE", self.data_path)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        self.tempdir.cleanup()

    def test_list_tasks_filters_by_status(self):
        tasks = service.list_tasks(status="open")
        self.assertEqual([task["id"] for task in tasks], [1, 3])

    def test_list_tasks_filters_by_q_case_insensitive_across_title_and_description(self):
        tasks = service.list_tasks(q="launch")
        self.assertEqual([task["id"] for task in tasks], [1])

        tasks = service.list_tasks(q="OAUTH")
        self.assertEqual([task["id"] for task in tasks], [2])

    def test_list_tasks_filters_by_status_and_q(self):
        tasks = service.list_tasks(status="open", q="plan")
        self.assertEqual([task["id"] for task in tasks], [3])

    def test_complete_task_persists_status_and_timestamp(self):
        updated = service.complete_task(1)

        self.assertEqual(updated["status"], "done")
        self.assertIsNotNone(updated["completed_at"])

        persisted = store.load_tasks()
        self.assertEqual(persisted[0]["status"], "done")
        self.assertIsNotNone(persisted[0]["completed_at"])


if __name__ == "__main__":
    unittest.main()
