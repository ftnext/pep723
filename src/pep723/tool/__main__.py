import io
import sys
import tempfile
import tokenize

from packaging.specifiers import InvalidSpecifier, Specifier
from packaging.version import InvalidVersion, Version

from pep723.parser import parse
from pep723.tool import venv
from pep723.tool.cli import AddArgs, parse_args
from pep723.tool.runner import run
from pep723.writer import add_dependencies

args = parse_args()

if isinstance(args, AddArgs):
    if args.python:
        try:
            Version(args.python)
            Specifier(f">={args.python}")
        except (InvalidVersion, InvalidSpecifier):
            print(
                f"Error: --python requires a bare version number "
                f"(e.g. '3.13'), got '{args.python}'",
                file=sys.stderr,
            )
            sys.exit(1)
    raw = args.script.read_bytes()
    encoding = tokenize.detect_encoding(io.BytesIO(raw).readline)[0]
    script_text = raw.decode(encoding)
    crlf = "\r\n" in script_text
    if crlf:
        script_text = script_text.replace("\r\n", "\n")
    requires_python = f">={args.python}" if args.python else None
    updated = add_dependencies(script_text, args.dependencies, requires_python)
    if crlf:
        updated = updated.replace("\n", "\r\n")
    args.script.write_text(updated, encoding=encoding, newline="")
else:
    metadata = parse(args.script.read_text())
    with tempfile.TemporaryDirectory() as tmpdir:
        venv.create_with_dependencies(tmpdir, metadata["dependencies"])
        run(f"{tmpdir}/bin/python", str(args.script))
