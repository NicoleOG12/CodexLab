from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from app.schemas import TaskStatus
from app.service import complete_task, get_task, list_tasks
from app.store import save_tasks


class ListTasksTests(TestCase):
    def setUp(self) -> None:
        self.tasks = [
            {
                "id": 1,
                "status": "open",
                "title": "Write launch recap",
                "description": "Draft a short internal summary.",
            },
            {
                "id": 2,
                "status": "done",
                "title": "Fix login redirect",
                "description": "Resolve the OAuth callback issue.",
            },
            {
                "id": 3,
                "status": "open",
                "title": "Plan workshop agenda",
                "description": "Outline the partner session.",
            },
        ]
        self.load_tasks_patcher = patch("app.service.load_tasks", return_value=self.tasks)
        self.load_tasks_patcher.start()
        self.addCleanup(self.load_tasks_patcher.stop)

    def test_filters_open_tasks(self) -> None:
        self.assertEqual(list_tasks(status=TaskStatus.open), [self.tasks[0], self.tasks[2]])

    def test_filters_done_tasks(self) -> None:
        self.assertEqual(list_tasks(status=TaskStatus.done), [self.tasks[1]])

    def test_returns_all_tasks_without_status_filter(self) -> None:
        self.assertEqual(list_tasks(), self.tasks)

    def test_searches_titles_case_insensitively(self) -> None:
        self.assertEqual(list_tasks(q="LAUNCH"), [self.tasks[0]])

    def test_searches_descriptions_case_insensitively(self) -> None:
        self.assertEqual(list_tasks(q="oAuTh"), [self.tasks[1]])

    def test_combines_status_and_search_filters(self) -> None:
        self.assertEqual(list_tasks(status=TaskStatus.open, q="PLAN"), [self.tasks[2]])

    def test_returns_no_tasks_when_search_does_not_match(self) -> None:
        self.assertEqual(list_tasks(q="missing"), [])


class CompleteTaskTests(TestCase):
    def setUp(self) -> None:
        self.temp_dir = TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.data_file_patcher = patch(
            "app.store.DATA_FILE",
            Path(self.temp_dir.name) / "tasks.json",
        )
        self.data_file_patcher.start()
        self.addCleanup(self.data_file_patcher.stop)
        save_tasks(
            [
                {
                    "id": 1,
                    "title": "Persist completion",
                    "description": "",
                    "status": "open",
                    "priority": "medium",
                    "created_at": "2026-02-25T16:00:00+00:00",
                    "completed_at": None,
                }
            ]
        )

    def test_completion_is_persisted(self) -> None:
        completed = complete_task(1)

        self.assertIsNotNone(completed)
        self.assertEqual(completed["status"], "done")
        self.assertIsNotNone(completed["completed_at"])

        fetched = get_task(1)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched["status"], "done")
        self.assertEqual(fetched["completed_at"], completed["completed_at"])
