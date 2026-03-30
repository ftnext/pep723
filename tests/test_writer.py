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
            """\
# /// script
# dependencies = [
#   "zope.interface",
# ]
# ///
""",
            ["zope_interface"],
            """\
# /// script
# dependencies = [
#   "zope.interface",
# ]
# ///
""",
        ),
        (
            """\
# /// script
# dependencies = [
#   "importlib-metadata; python_version < '3.10'",
# ]
# ///
""",
            ["importlib-metadata; python_version >= '3.10'"],
            """\
# /// script
# dependencies = [
#   "importlib-metadata; python_version < '3.10'",
#   "importlib-metadata; python_version >= '3.10'",
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
        (
            script_with_block,
            ["httpx[http2]"],
            """\
# /// script
# dependencies = [
#   "httpx",
#   "rich",
#   "httpx[http2]",
# ]
# ///

import httpx
""",
        ),
        (
            """\
#!/usr/bin/env python
import time
""",
            ["requests"],
            """\
#!/usr/bin/env python

# /// script
# dependencies = [
#   "requests",
# ]
# ///
import time
""",
        ),
        (
            "#!/usr/bin/env python",
            ["requests"],
            """\
#!/usr/bin/env python

# /// script
# dependencies = [
#   "requests",
# ]
# ///
""",
        ),
        (
            """\
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
""",
            ["requests"],
            """\
#!/usr/bin/env python
# -*- coding: utf-8 -*-

# /// script
# dependencies = [
#   "requests",
# ]
# ///
import sys
""",
        ),
    ],
    ids=[
        "add new dep to existing block",
        "skip exact duplicate",
        "skip case-insensitive duplicate",
        "skip hyphen-underscore normalized duplicate",
        "skip dot-underscore normalized duplicate",
        "marker-specific requirements are distinct",
        "create new block when missing",
        "create block for empty script",
        "deduplicate in new_deps",
        "create dependencies key when block has none",
        "extras variant is not a duplicate of bare package",
        "preserve shebang when inserting new block",
        "preserve shebang-only file when inserting new block",
        "preserve shebang and encoding cookie",
    ],
)
def test_add_dependencies(
    script: str, new_deps: list[str], expected: str
) -> None:
    assert add_dependencies(script, new_deps) == expected


def test_raise_error_when_multiple_script_blocks_found() -> None:
    script = """\
# /// script
# dependencies = ["httpx"]
# ///

# /// script
# dependencies = ["rich"]
# ///
"""
    with pytest.raises(ValueError):
        add_dependencies(script, ["requests"])
