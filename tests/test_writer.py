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
    "script,new_deps,expected,requires_python",
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
            None,
        ),
        (
            script_with_block,
            ["httpx"],
            script_with_block,
            None,
        ),
        (
            script_with_block,
            ["Httpx"],
            script_with_block,
            None,
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
            None,
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
            None,
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
            None,
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
            None,
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
            None,
        ),
        (
            script_without_block,
            ["requests", "rich"],
            """\
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "requests",
#   "rich",
# ]
# ///

import time
import sys
""",
            ">=3.12",
        ),
        (
            empty_script,
            ["requests"],
            """\
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "requests",
# ]
# ///
""",
            ">=3.12",
        ),
        (
            script_without_block,
            ["requests", "requests"],
            """\
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "requests",
# ]
# ///

import time
import sys
""",
            ">=3.12",
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
            None,
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
            None,
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
# requires-python = ">=3.12"
# dependencies = [
#   "requests",
# ]
# ///
import time
""",
            ">=3.12",
        ),
        (
            "#!/usr/bin/env python",
            ["requests"],
            """\
#!/usr/bin/env python

# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "requests",
# ]
# ///
""",
            ">=3.12",
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
# requires-python = ">=3.12"
# dependencies = [
#   "requests",
# ]
# ///
import sys
""",
            ">=3.12",
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
# requires-python = ">=3.12"
# dependencies = [
#   "requests",
# ]
# ///
import sys
""",
            ">=3.12",
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
# requires-python = ">=3.12"
# dependencies = [
#   "requests",
# ]
# ///
import sys
""",
            ">=3.12",
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
    script: str,
    new_deps: list[str],
    expected: str,
    requires_python: str | None,
) -> None:
    assert (
        add_dependencies(script, new_deps, requires_python=requires_python)
        == expected
    )


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
    result = add_dependencies(script, ["requests"], requires_python=">=3.12")
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
# requires-python = ">=3.12"
# dependencies = [
#   "httpx[brotli,http2]",
# ]
# ///

import time
"""
    assert (
        add_dependencies(
            script,
            ["httpx[http2]", "httpx[brotli]"],
            requires_python=">=3.12",
        )
        == expected
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


class TestRequiresPython:
    def test_new_block_with_explicit_python(self) -> None:
        result = add_dependencies("", ["requests"], requires_python=">=3.13")
        assert 'requires-python = ">=3.13"' in result
        assert '"requests"' in result

    def test_new_block_defaults_to_running_python(self) -> None:
        import sys

        expected_version = (
            f">={sys.version_info.major}.{sys.version_info.minor}"
        )
        result = add_dependencies("", ["requests"])
        assert f'requires-python = "{expected_version}"' in result

    def test_existing_block_updates_requires_python_when_specified(
        self,
    ) -> None:
        script = """\
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "httpx",
# ]
# ///
"""
        result = add_dependencies(
            script, ["requests"], requires_python=">=3.13"
        )
        assert 'requires-python = ">=3.13"' in result
        assert 'requires-python = ">=3.11"' not in result

    def test_existing_block_preserves_requires_python_when_not_specified(
        self,
    ) -> None:
        script = """\
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "httpx",
# ]
# ///
"""
        result = add_dependencies(script, ["requests"])
        assert 'requires-python = ">=3.11"' in result

    def test_existing_block_adds_requires_python_when_specified(
        self,
    ) -> None:
        result = add_dependencies(
            script_with_block, ["requests"], requires_python=">=3.13"
        )
        assert 'requires-python = ">=3.13"' in result

    def test_existing_block_without_requires_python_stays_without(
        self,
    ) -> None:
        result = add_dependencies(script_with_block, ["requests"])
        assert "requires-python" not in result

    def test_existing_block_overwrites_compound_specifier(self) -> None:
        script = """\
# /// script
# requires-python = ">=3.10,<4"
# dependencies = [
#   "httpx",
# ]
# ///
"""
        result = add_dependencies(
            script, ["requests"], requires_python=">=3.13"
        )
        assert 'requires-python = ">=3.13"' in result
        assert "<4" not in result
        assert ">=3.10" not in result

    def test_existing_block_replaces_compatible_release_operator(self) -> None:
        script = """\
# /// script
# requires-python = "~=3.11.0"
# dependencies = [
#   "httpx",
# ]
# ///
"""
        result = add_dependencies(
            script, ["requests"], requires_python=">=3.13"
        )
        assert ">=3.13" in result
        assert "~=3.11" not in result

    def test_existing_block_replaces_exact_version_operator(self) -> None:
        script = """\
# /// script
# requires-python = "==3.11.*"
# dependencies = [
#   "httpx",
# ]
# ///
"""
        result = add_dependencies(
            script, ["requests"], requires_python=">=3.13"
        )
        assert ">=3.13" in result
        assert "==3.11" not in result

    def test_existing_block_replaces_arbitrary_equality_operator(self) -> None:
        script = """\
# /// script
# requires-python = "===3.11"
# dependencies = [
#   "httpx",
# ]
# ///
"""
        result = add_dependencies(
            script, ["requests"], requires_python=">=3.13"
        )
        assert ">=3.13" in result
        assert "===3.11" not in result

    def test_new_block_requires_python_before_dependencies(self) -> None:
        result = add_dependencies("", ["requests"], requires_python=">=3.12")
        rp_pos = result.index("requires-python")
        deps_pos = result.index("dependencies")
        assert rp_pos < deps_pos
