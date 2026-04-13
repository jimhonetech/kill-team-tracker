"""QA tests that validate baseline pytest automation expectations."""

from __future__ import annotations

import subprocess
import sys


def test_pytest_command_returns_zero_for_passing_subset() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_basic.py", "-q"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr


def test_pytest_returns_non_zero_for_failing_test_in_automation_context(
    tmp_path,
) -> None:
    failing_test = tmp_path / "test_intentional_failure.py"
    failing_test.write_text(
        "def test_intentional_failure():\n"
        "    assert False, 'intentional failure for exit-code validation'\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, "-m", "pytest", str(failing_test), "-q"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "intentional failure for exit-code validation" in (
        result.stdout + result.stderr
    )
