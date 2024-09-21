import tempfile

from pep723.parser import parse
from pep723.tool import venv
from pep723.tool.cli import parse_args
from pep723.tool.runner import run

args = parse_args()
metadata = parse(args.script.read_text())
with tempfile.TemporaryDirectory() as tmpdir:
    venv.create_with_dependencies(tmpdir, metadata["dependencies"])
    run(f"{tmpdir}/bin/python", str(args.script))
