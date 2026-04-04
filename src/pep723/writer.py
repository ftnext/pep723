from __future__ import annotations

import re
import sys
from collections.abc import Sequence
from typing import Any, cast

import tomlkit
from packaging.requirements import InvalidRequirement, Requirement
from packaging.utils import canonicalize_name

from pep723.parser import REGEX

_CODING_RE = re.compile(r"^[ \t\f]*#.*?coding[:=][ \t]*([-\w.]+)", re.ASCII)


def _merge_key(
    requirement: Requirement,
) -> tuple[str, str, str | None, str | None]:
    return (
        canonicalize_name(requirement.name),
        str(requirement.specifier),
        requirement.url,
        None if requirement.marker is None else str(requirement.marker),
    )


def _merge_requirement_strings(existing: str, incoming: str) -> str:
    existing_req = _parse_requirement(existing, "existing dependency")
    incoming_req = _parse_requirement(incoming, "new dependency")

    if _merge_key(existing_req) != _merge_key(incoming_req):
        return existing

    merged_extras = sorted(existing_req.extras | incoming_req.extras)
    if merged_extras == sorted(existing_req.extras):
        return existing

    requirement = existing_req.name
    if merged_extras:
        requirement += f"[{','.join(merged_extras)}]"
    requirement += str(existing_req.specifier)
    if existing_req.url is not None:
        requirement += f" @ {existing_req.url}"
    if existing_req.marker is not None:
        requirement += f"; {existing_req.marker}"
    return requirement


def _parse_requirement(dep: str, source: str) -> Requirement:
    try:
        return Requirement(dep)
    except InvalidRequirement as exc:
        raise ValueError(f"Invalid {source}: {dep!r}") from exc


def _merge_into_requirements_list(
    deps: list[str], dep: str, dep_source: str, existing_source: str
) -> None:
    req = _parse_requirement(dep, dep_source)
    key = _merge_key(req)
    for index, existing in enumerate(deps):
        existing_req = _parse_requirement(existing, existing_source)
        if _merge_key(existing_req) == key:
            deps[index] = _merge_requirement_strings(existing, dep)
            break
    else:
        deps.append(dep)


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


def _deduplicate(deps: Sequence[str]) -> list[str]:
    result: list[str] = []
    for dep in deps:
        _merge_into_requirements_list(
            result,
            dep,
            "new dependency",
            "new dependency",
        )
    return result


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


def _default_requires_python() -> str:
    return f">={sys.version_info.major}.{sys.version_info.minor}"


def _merge_requires_python(existing: str, incoming: str) -> str:
    """Replace *existing* requires-python with *incoming* value.

    When ``--python`` is explicitly specified, the existing
    ``requires-python`` is unconditionally overwritten with the new value
    regardless of the specifier form (``~=``, ``==.*``, ``>=``, etc.).
    """
    return incoming


def add_dependencies(
    script: str,
    new_deps: Sequence[str],
    requires_python: str | None = None,
) -> str:
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
        for dep in new_deps:
            _merge_into_requirements_list(
                existing_deps,
                dep,
                "new dependency",
                "dependency in script block",
            )
        if requires_python is not None:
            existing_rp = config.get("requires-python")
            if existing_rp is not None:
                config["requires-python"] = _merge_requires_python(
                    str(existing_rp), requires_python
                )
            else:
                config["requires-python"] = requires_python
        new_content = _add_comment_prefix(tomlkit.dumps(config))
        start, end = match.span("content")
        return script[:start] + new_content + script[end:]

    if requires_python is None:
        requires_python = _default_requires_python()

    deduped = _deduplicate(new_deps)
    rp_line = f'requires-python = "{requires_python}"\n'
    deps_lines = ["dependencies = [\n"]
    for dep in deduped:
        deps_lines.append(f'  "{dep}",\n')
    deps_lines.append("]\n")
    content = _add_comment_prefix(rp_line + "".join(deps_lines))
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
