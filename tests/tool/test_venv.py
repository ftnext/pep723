import sys

from pep723.tool.venv import create_venv_with_dependencies


def test_create_venv_with_dependencies(tmp_path):
    # TODO: Without download from PyPI
    dependencies = ["kojo-fan-art"]
    create_venv_with_dependencies(tmp_path, dependencies)

    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    assert (
        tmp_path
        / "lib"
        / f"python{python_version}"
        / "site-packages"
        / "the_solitary_castle_in_the_mirror"
    ).exists()
