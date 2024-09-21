import re
import tomllib
from typing import TypedDict, cast

# ref: https://peps.python.org/pep-0723/#specification
REGEX = (
    r"(?m)^# /// (?P<type>[a-zA-Z0-9-]+)$\s(?P<content>(^#(| .*)$\s)+)^# ///$"
)


class ScriptMetadata(TypedDict):
    dependencies: list[str]


def parse(script: str) -> ScriptMetadata:
    name = "script"
    matches = list(
        filter(lambda m: m.group("type") == name, re.finditer(REGEX, script))
    )
    if len(matches) > 1:
        raise ValueError(
            f"Multiple {name} blocks found. You can write only one"
        )

    content = "".join(
        line[2:]
        for line in matches[0].group("content").splitlines(keepends=True)
    )
    return cast(ScriptMetadata, tomllib.loads(content))
