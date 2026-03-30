from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class RunArgs:
    script: Path


@dataclass
class AddArgs:
    script: Path
    dependencies: list[str]


_SUBCOMMANDS = {"run", "add"}


def parse_args() -> RunArgs | AddArgs:
    argv = sys.argv[1:]
    # Treat as subcommand only when enough args follow to satisfy it.
    # This preserves backward compat for scripts literally named
    # "run" or "add": `python -m pep723.tool add` runs script "add".
    is_subcommand = False
    if argv and argv[0] in _SUBCOMMANDS:
        if argv[0] == "add" and len(argv) >= 3:
            is_subcommand = True
        elif argv[0] == "run" and len(argv) >= 2:
            is_subcommand = True
    if not is_subcommand:
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
            script=args.script,
            dependencies=args.dependencies,
        )
    return RunArgs(script=args.script)
