import unittest
from pathlib import Path
import runpy
from unittest.mock import patch

import main


class FakeApplication:
    created_with: list[str] | None = None

    def __init__(self, argv: list[str]) -> None:
        self.__class__.created_with = argv

    def exec(self) -> int:
        return 7


class FakeMainWindow:
    shown = False

    def show(self) -> None:
        self.__class__.shown = True


class MainEntrypointTests(unittest.TestCase):
    def test_main_creates_application_window_and_returns_exit_code(self) -> None:
        FakeApplication.created_with = None
        FakeMainWindow.shown = False

        with (
            patch("main.QApplication", FakeApplication),
            patch("main.MainWindow", FakeMainWindow),
        ):
            exit_code = main.main(["projectllm"])

        self.assertEqual(exit_code, 7)
        self.assertEqual(FakeApplication.created_with, ["projectllm"])
        self.assertTrue(FakeMainWindow.shown)

    def test_module_entrypoint_exposes_main_without_running_guard(self) -> None:
        namespace = runpy.run_path(str(Path("__main__.py")), run_name="projectllm_test")

        self.assertIs(namespace["main"], main.main)


if __name__ == "__main__":
    unittest.main()
