from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from pep723.parser import parse

if TYPE_CHECKING:
    from pep723.parser import ScriptMetadata

single_line_dependencies_script = """\
# /// script
# dependencies = ["rich"]
# ///
import time
from rich.progress import track

for i in track(range(20), description="For example:"):
    time.sleep(0.05)\
"""
multiple_lines_dependencies_script = """\
# /// script
# dependencies = [
#   "requests<3",
#   "rich",
# ]
# ///\
"""

# >otherwise just the first character
# >(which means the line consists of only a single #)
# ref: https://peps.python.org/pep-0723/#specification
empty_line_metadata_script = """\
# /// script
#
# dependencies = [
#
#   "httpx",
#
# ]
# ///\
"""


@pytest.mark.parametrize(
    "script,expected",
    [
        (single_line_dependencies_script, {"dependencies": ["rich"]}),
        (
            multiple_lines_dependencies_script,
            {"dependencies": ["requests<3", "rich"]},
        ),
        (empty_line_metadata_script, {"dependencies": ["httpx"]}),
    ],
    ids=[
        "single line dependencies",
        "multiple line dependencies",
        "empty line metadata",
    ],
)
def test_parse(script: str, expected: ScriptMetadata) -> None:
    assert parse(script) == expected


def test_raise_error_when_multiple_scripts_found() -> None:
    script = """\
# /// script
# dependencies = [
#   "requests<3",
# ]
# ///

# /// script
# dependencies = [
#   "rich",
# ]
# ///\
"""
    with pytest.raises(ValueError):
        parse(script)
