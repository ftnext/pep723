import sys
from pathlib import Path

from pep723.tool.venv import create_with_dependencies


def site_packages_dir(venv_path: Path) -> Path:
    if sys.platform == "win32":
        return venv_path / "Lib" / "site-packages"

    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    return venv_path / "lib" / f"python{python_version}" / "site-packages"


def test_create_venv_with_dependencies(tmp_path):
    # TODO: Without download from PyPI
    dependencies = ["kojo-fan-art"]
    create_with_dependencies(tmp_path, dependencies)

    assert (
        site_packages_dir(tmp_path) / "the_solitary_castle_in_the_mirror"
    ).exists()
