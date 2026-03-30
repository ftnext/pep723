from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def python_files() -> list[str]:
    files = sorted(ROOT.joinpath("src").rglob("*.py"))
    files.extend(sorted(ROOT.joinpath("tests").rglob("*.py")))
    files.append(ROOT / "setup.py")
    return [str(path.relative_to(ROOT)) for path in files]


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python scripts/run_dev_tool.py [autoflake|pyupgrade]")
        return 1

    tool = sys.argv[1]
    files = python_files()

    commands = {
        "autoflake": [
            sys.executable,
            "-m",
            "autoflake",
            "--in-place",
            "--remove-all-unused-imports",
            *files,
        ],
        "pyupgrade": [sys.executable, "-m", "pyupgrade", *files],
    }

    try:
        command = commands[tool]
    except KeyError:
        print(f"unsupported tool: {tool}")
        return 1

    return subprocess.run(command, cwd=ROOT, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
