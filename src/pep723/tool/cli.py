import argparse
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Args:
    script: Path


def parse_args() -> type[Args]:
    parser = argparse.ArgumentParser()
    parser.add_argument("script", type=Path)
    return parser.parse_args(namespace=Args)
