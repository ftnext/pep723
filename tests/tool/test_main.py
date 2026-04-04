from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture
def tmp_script(tmp_path: Path) -> Path:
    script = tmp_path / "script.py"
    script.write_text("import sys\n")
    return script


@pytest.mark.parametrize(
    "python_arg",
    [
        "<3.13",
        ">=3.13",
        "<=3.13",
        "!=3.13",
        ">3.13,<3.14",
        "~=3.13",
        ">=<3.13",
    ],
    ids=[
        "less-than",
        "greater-equal",
        "less-equal",
        "not-equal",
        "compound-specifier",
        "compatible-release",
        "double-specifier",
    ],
)
def test_python_flag_rejects_specifier(
    tmp_script: Path, python_arg: str
) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pep723.tool",
            "add",
            "--python",
            python_arg,
            str(tmp_script),
            "requests",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "bare version number" in result.stderr


@pytest.mark.parametrize(
    "python_arg",
    ["3.13", "3", "3.13.1"],
    ids=["major-minor", "major-only", "major-minor-patch"],
)
def test_python_flag_accepts_bare_version(
    tmp_script: Path, python_arg: str
) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pep723.tool",
            "add",
            "--python",
            python_arg,
            str(tmp_script),
            "requests",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
