from __future__ import annotations

import re
from collections.abc import Sequence
from typing import Any, cast

import tomlkit

from pep723.parser import REGEX


def _pkg_name(specifier: str) -> str:
    return (
        re.split(r"[<>=!~;\[,\s]", specifier, maxsplit=1)[0]
        .lower()
        .replace("-", "_")
    )


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
    match = re.search(REGEX, script)

    if match:
        content = _strip_comment_prefix(match.group("content"))
        config = tomlkit.parse(content)
        existing_deps = cast(list[Any], config["dependencies"])
        existing_names = {_pkg_name(d) for d in existing_deps}
        for dep in new_deps:
            if _pkg_name(dep) not in existing_names:
                existing_deps.append(dep)
                existing_names.add(_pkg_name(dep))
        new_content = _add_comment_prefix(tomlkit.dumps(config))
        start, end = match.span("content")
        return script[:start] + new_content + script[end:]
    else:
        seen_names: set[str] = set()
        deduped: list[str] = []
        for dep in new_deps:
            name = _pkg_name(dep)
            if name not in seen_names:
                deduped.append(dep)
                seen_names.add(name)
        deps_lines = ["dependencies = [\n"]
        for dep in deduped:
            deps_lines.append(f'  "{dep}",\n')
        deps_lines.append("]\n")
        content = _add_comment_prefix("".join(deps_lines))
        block = f"# /// script\n{content}# ///\n"
        if script:
            return block + "\n" + script
        return block
