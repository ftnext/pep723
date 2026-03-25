from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path


@dataclass
class RunArgs:
    command: str
    script: Path


@dataclass
class AddArgs:
    command: str
    script: Path
    dependencies: list[str]


def parse_args() -> RunArgs | AddArgs:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("script", type=Path)

    add_parser = subparsers.add_parser("add")
    add_parser.add_argument("script", type=Path)
    add_parser.add_argument("dependencies", nargs="+")

    args = parser.parse_args()
    if args.command == "add":
        return AddArgs(
            command=args.command,
            script=args.script,
            dependencies=args.dependencies,
        )
    return RunArgs(command=args.command, script=args.script)
