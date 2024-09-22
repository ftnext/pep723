import pytest

from pep723.parser import parse

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


@pytest.mark.parametrize(
    "script,expected",
    [
        (single_line_dependencies_script, {"dependencies": ["rich"]}),
        (
            multiple_lines_dependencies_script,
            {"dependencies": ["requests<3", "rich"]},
        ),
    ],
    ids=[
        "single line dependencies",
        "multiple line dependencies",
    ],
)
def test_parse(script, expected):
    assert parse(script) == expected


def test_raise_error_when_multiple_scripts_found():
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
