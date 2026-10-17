import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from app import service, store
from app.schemas import TaskStatus


class TaskServiceTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        data_file = Path(directory.name) / "tasks.json"
        self.tasks = [
            {
                "id": 1,
                "title": "Open task",
                "description": "",
                "status": "open",
                "priority": "medium",
                "created_at": "2026-02-25T16:00:00+00:00",
                "completed_at": None,
            },
            {
                "id": 2,
                "title": "Done task",
                "description": "",
                "status": "done",
                "priority": "high",
                "created_at": "2026-02-20T14:30:00+00:00",
                "completed_at": "2026-02-21T09:15:00+00:00",
            },
        ]
        data_file.write_text(json.dumps(self.tasks), encoding="utf-8")
        patcher = patch.object(store, "DATA_FILE", data_file)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_list_without_status_returns_all_tasks(self):
        self.assertEqual(service.list_tasks(), self.tasks)

    def test_list_filters_by_each_status(self):
        for status in TaskStatus:
            with self.subTest(status=status):
                expected = [task for task in self.tasks if task["status"] == status]
                self.assertEqual(service.list_tasks(status=status), expected)

    def test_list_returns_empty_when_no_tasks_match(self):
        store.save_tasks([self.tasks[1]])
        self.assertEqual(service.list_tasks(status=TaskStatus.open), [])

    def test_search_matches_title_substrings_case_insensitively(self):
        self.assertEqual(service.list_tasks(q="pEn Ta"), [self.tasks[0]])

    def test_search_matches_description_substrings_case_insensitively(self):
        self.tasks[1]["description"] = "Draft the LAUNCH summary"
        store.save_tasks(self.tasks)
        self.assertEqual(service.list_tasks(q="LaUnCh"), [self.tasks[1]])

    def test_search_combines_with_status(self):
        for status, expected in (
            (TaskStatus.open, [self.tasks[0]]),
            (TaskStatus.done, [self.tasks[1]]),
        ):
            with self.subTest(status=status):
                self.assertEqual(service.list_tasks(status=status, q="TASK"), expected)
        self.assertEqual(service.list_tasks(status=TaskStatus.done, q="open"), [])

    def test_search_returns_empty_when_neither_field_matches(self):
        self.assertEqual(service.list_tasks(q="missing"), [])

    def test_search_does_not_match_across_field_boundaries(self):
        self.tasks[0]["description"] = "summary"
        store.save_tasks(self.tasks)
        self.assertEqual(service.list_tasks(q="task summary"), [])

    def test_completion_persists_status_and_timestamp(self):
        completed = service.complete_task(1)
        self.assertIsNotNone(completed)
        self.assertEqual(completed["status"], "done")
        self.assertIsNotNone(completed["completed_at"])
        self.assertIsNotNone(datetime.fromisoformat(completed["completed_at"]).tzinfo)
        self.assertEqual(service.get_task(1), completed)
        self.assertEqual(store.load_tasks(), [completed, self.tasks[1]])
        for field in ("id", "title", "description", "priority", "created_at"):
            self.assertEqual(completed[field], self.tasks[0][field])
        self.assertEqual(service.list_tasks(status=TaskStatus.open), [])
        self.assertEqual(service.list_tasks(status=TaskStatus.done), store.load_tasks())

    def test_missing_task_does_not_change_storage(self):
        self.assertIsNone(service.complete_task(999))
        self.assertIsNone(service.get_task(999))
        self.assertEqual(store.load_tasks(), self.tasks)
