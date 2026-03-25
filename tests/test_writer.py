from __future__ import annotations

import pytest

from pep723.writer import add_dependencies

script_with_block = """\
# /// script
# dependencies = [
#   "httpx",
#   "rich",
# ]
# ///

import httpx
"""

script_without_block = """\
import time
import sys
"""

empty_script = ""


@pytest.mark.parametrize(
    "script,new_deps,expected",
    [
        (
            script_with_block,
            ["requests"],
            """\
# /// script
# dependencies = [
#   "httpx",
#   "rich",
#   "requests",
# ]
# ///

import httpx
""",
        ),
        (
            script_with_block,
            ["httpx"],
            script_with_block,
        ),
        (
            script_with_block,
            ["Httpx"],
            script_with_block,
        ),
        (
            """\
# /// script
# dependencies = [
#   "some-lib",
# ]
# ///
""",
            ["some_lib"],
            """\
# /// script
# dependencies = [
#   "some-lib",
# ]
# ///
""",
        ),
        (
            script_without_block,
            ["requests", "rich"],
            """\
# /// script
# dependencies = [
#   "requests",
#   "rich",
# ]
# ///

import time
import sys
""",
        ),
        (
            empty_script,
            ["requests"],
            """\
# /// script
# dependencies = [
#   "requests",
# ]
# ///
""",
        ),
        (
            script_without_block,
            ["requests", "requests"],
            """\
# /// script
# dependencies = [
#   "requests",
# ]
# ///

import time
import sys
""",
        ),
        (
            """\
# /// script
# requires-python = ">=3.11"
# ///
""",
            ["requests"],
            """\
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "requests",
# ]
# ///
""",
        ),
    ],
    ids=[
        "add new dep to existing block",
        "skip exact duplicate",
        "skip case-insensitive duplicate",
        "skip hyphen-underscore normalized duplicate",
        "create new block when missing",
        "create block for empty script",
        "deduplicate in new_deps",
        "create dependencies key when block has none",
    ],
)
def test_add_dependencies(
    script: str, new_deps: list[str], expected: str
) -> None:
    assert add_dependencies(script, new_deps) == expected
