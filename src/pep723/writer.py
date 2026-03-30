from __future__ import annotations

import re
from collections.abc import Sequence
from typing import Any, cast

import tomlkit

from pep723.parser import REGEX

_CODING_RE = re.compile(r"^[ \t\f]*#.*?coding[:=][ \t]*([-\w.]+)", re.ASCII)


def _pkg_key(specifier: str) -> str:
    """Build a canonical dedup key from a dependency specifier.

    Extras (e.g. requests[socks]) and environment markers
    (e.g. ; python_version < '3.10') are preserved so that distinct
    conditional requirements are NOT collapsed into one entry.
    """
    semicolon = specifier.find(";")
    if semicolon != -1:
        requirement = specifier[:semicolon]
        marker = specifier[semicolon:]
    else:
        requirement = specifier
        marker = ""
    raw_name = re.split(r"[<>=!~,\s]", requirement, maxsplit=1)[0]
    name = re.sub(r"[-_.]+", "_", raw_name).lower()
    if marker:
        return name + marker
    return name


def _strip_comment_prefix(content: str) -> str:
    return "".join(
        line[2:] if line.startswith("# ") else line[1:]
        for line in content.splitlines(keepends=True)
    )


def _add_comment_prefix(toml_str: str) -> str:
    return "".join(
        f"# {line}" if line.strip() else f"#{line}"
        for line in toml_str.splitlines(keepends=True)
    )


def _block_insert_pos(script: str) -> int:
    """Find the index at which a new PEP 723 block should be inserted.

    Skips shebang and PEP 263 encoding cookies so they stay in the
    first two lines where Python requires them.
    """
    pos = 0
    lines_checked = 0

    if script.startswith("#!"):
        nl = script.find("\n")
        if nl == -1:
            return len(script)
        pos = nl + 1
        lines_checked = 1

    check_pos = pos
    for _ in range(2 - lines_checked):
        nl = script.find("\n", check_pos)
        line = script[check_pos:nl] if nl != -1 else script[check_pos:]
        if _CODING_RE.match(line):
            return nl + 1 if nl != -1 else len(script)
        if nl == -1:
            break
        check_pos = nl + 1

    return pos


def add_dependencies(script: str, new_deps: Sequence[str]) -> str:
    it = (m for m in re.finditer(REGEX, script) if m.group("type") == "script")
    match = next(it, None)
    if match is not None and next(it, None) is not None:
        raise ValueError(
            "Multiple script blocks found. You can write only one"
        )

    if match:
        content = _strip_comment_prefix(match.group("content"))
        config = tomlkit.parse(content)
        if "dependencies" not in config:
            arr = tomlkit.array()
            arr.multiline(True)
            config.add("dependencies", arr)
        existing_deps = cast(list[Any], config["dependencies"])
        existing_names = {_pkg_key(d) for d in existing_deps}
        for dep in new_deps:
            key = _pkg_key(dep)
            if key not in existing_names:
                existing_deps.append(dep)
                existing_names.add(key)
        new_content = _add_comment_prefix(tomlkit.dumps(config))
        start, end = match.span("content")
        return script[:start] + new_content + script[end:]
    else:
        seen_names: set[str] = set()
        deduped: list[str] = []
        for dep in new_deps:
            name = _pkg_key(dep)
            if name not in seen_names:
                deduped.append(dep)
                seen_names.add(name)
        deps_lines = ["dependencies = [\n"]
        for dep in deduped:
            deps_lines.append(f'  "{dep}",\n')
        deps_lines.append("]\n")
        content = _add_comment_prefix("".join(deps_lines))
        block = f"# /// script\n{content}# ///\n"
        insert_at = _block_insert_pos(script)
        if insert_at > 0:
            prefix = script[:insert_at]
            if not prefix.endswith("\n"):
                prefix += "\n"
            return prefix + "\n" + block + script[insert_at:]
        if script:
            return block + "\n" + script
        return block
