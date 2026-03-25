import tempfile

from pep723.parser import parse
from pep723.tool import venv
from pep723.tool.cli import AddArgs, parse_args
from pep723.tool.runner import run
from pep723.writer import add_dependencies

args = parse_args()

if isinstance(args, AddArgs):
    updated = add_dependencies(args.script.read_text(), args.dependencies)
    args.script.write_text(updated)
else:
    metadata = parse(args.script.read_text())
    with tempfile.TemporaryDirectory() as tmpdir:
        venv.create_with_dependencies(tmpdir, metadata["dependencies"])
        run(f"{tmpdir}/bin/python", str(args.script))
