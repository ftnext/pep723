from pep723.parser import parse


def test_parse_dependencies():
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
