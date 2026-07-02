import sys

from pathlib import Path

import pytest

from dbrownell_Common import SubprocessEx


# ----------------------------------------------------------------------
@pytest.fixture(scope="session", autouse=True)
def build_grammar():
    python_filename = Path(__file__).parent.parent / "src" / "Grammar" / "Build.py"
    assert python_filename.is_file(), python_filename

    sys.stdout.write("\n\n")

    result = SubprocessEx.Stream(f'uv run "{python_filename}"', sys.stdout)
    assert result == 0
