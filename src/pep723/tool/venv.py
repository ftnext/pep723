from collections.abc import Iterable
from types import SimpleNamespace
from venv import EnvBuilder


class WithDependenciesEnvBuilder(EnvBuilder):
    def __init__(
        self, *args, dependencies: Iterable[str] | None = None, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self._dependencies = dependencies or []

    def post_setup(self, context: SimpleNamespace) -> None:
        commands = [context, "-m", "pip", "install", *self._dependencies]
        self._call_new_python(*commands)

    def _call_new_python(self, context, *py_args, **kwargs):
        # Avoid for mypy to raise [attr-defined] error
        # >error: "ShirabeEnvBuilder" has no attribute "_call_new_python"
        return super()._call_new_python(context, *py_args, **kwargs)


def create_with_dependencies(
    venv_path: str, dependencies: Iterable[str]
) -> None:
    builder = WithDependenciesEnvBuilder(
        dependencies=dependencies, with_pip=True
    )
    builder.create(venv_path)
