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


_SUBCOMMANDS = {"run", "add"}


def parse_args() -> RunArgs | AddArgs:
    import sys

    argv = sys.argv[1:]
    if not argv or argv[0] not in _SUBCOMMANDS or Path(argv[0]).exists():
        argv = ["run"] + argv

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("script", type=Path)

    add_parser = subparsers.add_parser("add")
    add_parser.add_argument("script", type=Path)
    add_parser.add_argument("dependencies", nargs="+")

    args = parser.parse_args(argv)
    if args.command == "add":
        return AddArgs(
            command=args.command,
            script=args.script,
            dependencies=args.dependencies,
        )
    return RunArgs(command=args.command, script=args.script)
