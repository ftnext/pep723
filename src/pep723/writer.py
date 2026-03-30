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
    name = (
        re.split(r"[<>=!~,\s]", requirement, maxsplit=1)[0]
        .lower()
        .replace("-", "_")
        .replace(".", "_")
    )
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


def add_dependencies(script: str, new_deps: Sequence[str]) -> str:
    matches = [
        m for m in re.finditer(REGEX, script) if m.group("type") == "script"
    ]
    if len(matches) > 1:
        raise ValueError(
            "Multiple script blocks found. You can write only one"
        )
    match = matches[0] if matches else None

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
            if _pkg_key(dep) not in existing_names:
                existing_deps.append(dep)
                existing_names.add(_pkg_key(dep))
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
        if script.startswith("#!"):
            newline_pos = script.find("\n")
            if newline_pos == -1:
                return script + "\n\n" + block
            insert_at = newline_pos + 1
            # Preserve encoding cookie on line 2 (must stay in first
            # two lines for Python to recognize it)
            second_line_end = script.find("\n", insert_at)
            if second_line_end != -1:
                second_line = script[insert_at:second_line_end]
            else:
                second_line = script[insert_at:]
            if _CODING_RE.match(second_line):
                insert_at = (
                    second_line_end + 1
                    if second_line_end != -1
                    else len(script)
                )
            return script[:insert_at] + "\n" + block + script[insert_at:]
        if script:
            return block + "\n" + script
        return block
