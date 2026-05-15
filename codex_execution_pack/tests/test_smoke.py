from __future__ import annotations

import subprocess
import sys


def test_package_imports() -> None:
    import revision_context  # noqa: F401


def test_smoke_command_runs() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "revision_context.cli", "smoke"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "revision_context smoke ok" in result.stdout
