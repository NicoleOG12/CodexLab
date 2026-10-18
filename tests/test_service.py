import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from app import service


class TaskServiceTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.data_file = Path(directory.name) / "tasks.json"
        self.tasks = [
            {"id": 1, "title": "Open task", "description": "Plan the launch", "status": "open", "completed_at": None},
            {"id": 2, "title": "Done task", "description": "Archive the report", "status": "done", "completed_at": "2026-01-01T00:00:00+00:00"},
        ]
        self.data_file.write_text(json.dumps(self.tasks), encoding="utf-8")
        patcher = patch("app.store.DATA_FILE", self.data_file)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_status_filter_and_unfiltered_list(self):
        self.assertEqual(service.list_tasks(), self.tasks)
        for status, task_id in (("open", 1), ("done", 2)):
            with self.subTest(status=status):
                self.assertEqual(
                    [task["id"] for task in service.list_tasks(status=status)],
                    [task_id],
                )

    def test_search_matches_title_and_description_case_insensitively(self):
        for query, expected_ids in (
            ("pEn", [1]),
            ("LAUNCH", [1]),
            ("REPORT", [2]),
            ("TaSk", [1, 2]),
            ("missing", []),
        ):
            with self.subTest(query=query):
                self.assertEqual(
                    [task["id"] for task in service.list_tasks(q=query)],
                    expected_ids,
                )

    def test_search_combines_with_status(self):
        self.assertEqual(service.list_tasks(status="open", q="TASK"), [self.tasks[0]])
        self.assertEqual(service.list_tasks(status="done", q="REPORT"), [self.tasks[1]])
        self.assertEqual(service.list_tasks(status="open", q="REPORT"), [])

    def test_completion_persists_and_preserves_other_tasks(self):
        completed = service.complete_task(1)
        self.assertEqual(completed["status"], "done")
        self.assertIsNotNone(datetime.fromisoformat(completed["completed_at"]).tzinfo)
        stored = json.loads(self.data_file.read_text(encoding="utf-8"))
        self.assertEqual(stored, [completed, self.tasks[1]])
        self.assertEqual(service.get_task(1), completed)
        self.assertEqual(service.list_tasks(status="open"), [])

    def test_missing_completion_does_not_change_storage(self):
        original = self.data_file.read_bytes()
        self.assertIsNone(service.complete_task(999))
        self.assertEqual(self.data_file.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
