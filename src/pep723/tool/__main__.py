import tempfile

from pep723.parser import parse
from pep723.tool.cli import parse_args
from pep723.tool.runner import run
from pep723.tool.venv import create_venv_with_dependencies

args = parse_args()
metadata = parse(args.script.read_text())
with tempfile.TemporaryDirectory() as tmpdir:
    create_venv_with_dependencies(tmpdir, metadata["dependencies"])
    run(f"{tmpdir}/bin/python", str(args.script))
