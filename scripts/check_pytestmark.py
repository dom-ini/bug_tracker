import ast
import itertools
import sys
import tomllib
from pathlib import Path
from typing import Any, Mapping, Sequence

ConfigT = Mapping[str, Any]

PYPROJECT_TOML = Path("pyproject.toml")


def get_project_config() -> ConfigT:
    """Read config from pyproject.toml"""
    if not PYPROJECT_TOML.exists():
        print("⚠️ WARNING: pyproject.toml not found!")
        return {}

    try:
        with open(PYPROJECT_TOML, "rb") as f:
            return tomllib.load(f)
    except Exception as e:
        print(f"❌ ERROR: Error reading pyproject.toml: {e}")
        return {}


def get_pytest_markers(config: ConfigT) -> Sequence[str]:
    """Read pytest markers from project config"""
    return config.get("tool", {}).get("pytest", {}).get("ini_options", {}).get("markers", [])


def get_test_files_globs(config: ConfigT) -> Sequence[str]:
    """Read pytest file patterns from project config"""
    return config.get("tool", {}).get("pytest", {}).get("ini_options", {}).get("python_files", [])


def get_pytestmark_nodes_from_file(filepath: Path) -> Sequence[str]:
    """Extracts all `pytest.mark.<marker>` values from a test file."""
    with open(filepath, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=filepath)

    pytest_marks = []
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "pytestmark":
                    if isinstance(node.value, ast.Attribute) and node.value.attr:
                        pytest_marks.append(node.value.attr)
                    elif isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute):
                        pytest_marks.append(node.value.func.attr)
    return pytest_marks


def get_expected_test_marker(filepath: Path, test_markers: Sequence[str]) -> str | None:
    """Returns a test marker relevant to the specified filepath."""
    for marker in test_markers:
        if marker in filepath.parts:
            return marker
    return None


def check_pytestmarks(root_dir: str, test_markers: Sequence[str], file_globs: Sequence[str]) -> bool:
    """Ensures that test files contain the correct pytestmark for their directory."""
    success = True

    files: Sequence[Path] = itertools.chain.from_iterable(Path(root_dir).rglob(pattern) for pattern in file_globs)

    for file in files:
        expected_marker = get_expected_test_marker(file, test_markers)
        if not expected_marker:
            continue

        pytest_marks = get_pytestmark_nodes_from_file(file)

        if expected_marker not in pytest_marks:
            print(f"❌ ERROR: {file} is missing pytest.mark.{expected_marker}")
            success = False

        for mark in pytest_marks:
            if mark in test_markers and mark != expected_marker:
                print(
                    f"❌ ERROR: {file} has incorrect pytestmark '{mark}', expected only 'pytest.mark.{expected_marker}'"
                )
                success = False

    return success


if __name__ == "__main__":
    project_config = get_project_config()
    markers = get_pytest_markers(project_config)
    test_files_globs = get_test_files_globs(project_config)
    tests_root_dir = sys.argv[1]

    if not check_pytestmarks(tests_root_dir, markers, test_files_globs):
        sys.exit(1)

    print("✅ All test files have correct pytest marks!")
