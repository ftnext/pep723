import tempfile
import tokenize

from pep723.parser import parse
from pep723.tool import venv
from pep723.tool.cli import AddArgs, parse_args
from pep723.tool.runner import run
from pep723.writer import add_dependencies

args = parse_args()

if isinstance(args, AddArgs):
    with open(args.script, "rb") as f:
        encoding = tokenize.detect_encoding(f.readline)[0]
    script_text = args.script.read_text(encoding=encoding)
    updated = add_dependencies(script_text, args.dependencies)
    args.script.write_text(updated, encoding=encoding)
else:
    metadata = parse(args.script.read_text())
    with tempfile.TemporaryDirectory() as tmpdir:
        venv.create_with_dependencies(tmpdir, metadata["dependencies"])
        run(f"{tmpdir}/bin/python", str(args.script))
