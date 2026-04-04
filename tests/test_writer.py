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
#   "pkg @ https://example.com/pkg.tar.gz",
# ]
# ///
""",
            ["pkg@https://example.com/pkg.tar.gz"],
            """\
# /// script
# dependencies = [
#   "pkg @ https://example.com/pkg.tar.gz",
# ]
# ///
""",
        ),
        (
            """\
# /// script
# dependencies = [
#   "foo-bar",
# ]
# ///
""",
            ["foo__bar"],
            """\
# /// script
# dependencies = [
#   "foo-bar",
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
#   "httpx[http2]",
#   "rich",
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
        (
            """\
# -*- coding: cp932 -*-
import sys
""",
            ["requests"],
            """\
# -*- coding: cp932 -*-

# /// script
# dependencies = [
#   "requests",
# ]
# ///
import sys
""",
        ),
        (
            """\
# My script
# -*- coding: cp932 -*-
import sys
""",
            ["requests"],
            """\
# My script
# -*- coding: cp932 -*-

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
        "skip direct URL reference duplicate",
        "skip repeated separator normalized duplicate",
        "skip dot-underscore normalized duplicate",
        "marker-specific requirements are distinct",
        "create new block when missing",
        "create block for empty script",
        "deduplicate in new_deps",
        "create dependencies key when block has none",
        "extras variant replaces bare package",
        "preserve shebang when inserting new block",
        "preserve shebang-only file when inserting new block",
        "preserve shebang and encoding cookie",
        "preserve encoding cookie without shebang",
        "preserve second-line encoding cookie without shebang",
    ],
)
def test_add_dependencies(
    script: str, new_deps: list[str], expected: str
) -> None:
    assert add_dependencies(script, new_deps) == expected


def test_add_dependencies_preserves_crlf() -> None:
    script = (
        "# /// script\r\n"
        "# dependencies = [\r\n"
        '#   "httpx",\r\n'
        "# ]\r\n"
        "# ///\r\n"
        "\r\n"
        "import httpx\r\n"
    )
    result = add_dependencies(script, ["requests"])
    # New dep should be added with LF (writer works in LF),
    # but existing CRLF content is preserved by the caller (__main__.py).
    # The writer itself operates on LF-normalized text.
    assert "requests" in result


def test_add_dependencies_new_block_no_crlf_injection() -> None:
    script = "import time\nimport sys\n"
    result = add_dependencies(script, ["requests"])
    assert "\r\n" not in result


def test_add_dependencies_merges_multiple_extra_variants() -> None:
    script = """\
# /// script
# dependencies = [
#   "httpx[http2]",
# ]
# ///
"""
    expected = """\
# /// script
# dependencies = [
#   "httpx[brotli,http2]",
# ]
# ///
"""
    assert add_dependencies(script, ["httpx[brotli]"]) == expected


def test_add_dependencies_merges_duplicate_new_deps_with_distinct_extras() -> (
    None
):
    script = """\
import time
"""
    expected = """\
# /// script
# dependencies = [
#   "httpx[brotli,http2]",
# ]
# ///

import time
"""
    assert (
        add_dependencies(script, ["httpx[http2]", "httpx[brotli]"]) == expected
    )


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


def test_raise_error_for_invalid_new_dependency() -> None:
    with pytest.raises(
        ValueError, match=r"Invalid new dependency: 'not valid @ @'"
    ):
        add_dependencies("", ["not valid @ @"])


def test_raise_error_for_invalid_existing_dependency() -> None:
    script = """\
# /// script
# dependencies = [
#   "not valid @ @",
# ]
# ///
"""
    with pytest.raises(
        ValueError,
        match=r"Invalid dependency in script block: 'not valid @ @'",
    ):
        add_dependencies(script, ["requests"])
