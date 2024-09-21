import pytest

from pep723.parser import parse


def test_parse_dependencies_single_line():
    script = """\
# /// script
# dependencies = ["rich"]
# ///
import time
from rich.progress import track

for i in track(range(20), description="For example:"):
    time.sleep(0.05)\
"""

    assert parse(script) == {"dependencies": ["rich"]}


def test_parse_dependencies_multiple_line():
    script = """\
# /// script
# dependencies = [
#   "requests<3",
#   "rich",
# ]
# ///\
"""

    assert parse(script) == {"dependencies": ["requests<3", "rich"]}


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
