import os


def run(python_executable: str, script_path: str) -> None:
    env = dict(os.environ)
    os.execvpe("python", [python_executable, script_path], env)
