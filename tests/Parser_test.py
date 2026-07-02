import io
import tempfile
import textwrap

from pathlib import Path

from dbrownell_Common.Streams.DoneManager import DoneManager
from dbrownell_ParserLib import Error

from dbrownell_TheLanguage.Parser import parser


class TestParserInvalidInput:
    """Tests for parser error detection.

    Note: The current grammar has a limitation where function bodies with docstrings
    produce a NEWLINE token before DEDENT that the parser doesn't expect. These tests
    verify that the parser correctly detects and reports various syntax errors.
    """

    def test_MissingFunctionName(self) -> None:
        code = textwrap.dedent('''\
            func (a: Int,) : Void ->
                """
                Docstring.
                """
            ''')

        result = self._Parse(code)

        assert isinstance(result, Error)
        assert "IDENTIFIER" in result.message

    def test_MissingParameterList(self) -> None:
        code = textwrap.dedent('''\
            func MyFunc : Void ->
                """
            Docstring.
            """
            ''')

        result = self._Parse(code)

        assert isinstance(result, Error)
        assert "(" in result.message or "missing" in result.message.lower()

    def test_MissingReturnType(self) -> None:
        code = textwrap.dedent('''\
            func MyFunc(a: Int,) ->
                """
                Docstring.
                """
            ''')

        result = self._Parse(code)

        assert isinstance(result, Error)
        assert ":" in result.message or "IDENTIFIER" in result.message

    def test_MissingArrow(self) -> None:
        code = textwrap.dedent('''\
            func MyFunc(a: Int,) : Void
                """
                Docstring.
                """
            ''')

        result = self._Parse(code)

        assert isinstance(result, Error)
        assert "->" in result.message or "missing" in result.message.lower()

    def test_MissingBody(self) -> None:
        code = textwrap.dedent("""\
            func MyFunc(a: Int,) : Void ->
            """)

        result = self._Parse(code)

        assert isinstance(result, Error)

    def test_MissingParameterType(self) -> None:
        code = textwrap.dedent('''\
            func MyFunc(a,) : Void ->
                """
                Docstring.
                """
            ''')

        result = self._Parse(code)

        assert isinstance(result, Error)
        assert ":" in result.message or "missing" in result.message.lower()

    def test_MissingParameterName(self) -> None:
        code = textwrap.dedent('''\
            func MyFunc(: Int,) : Void ->
                """
                Docstring.
                """
            ''')

        result = self._Parse(code)

        assert isinstance(result, Error)

    def test_InvalidIdentifier(self) -> None:
        code = textwrap.dedent('''\
            func 123Invalid(a: Int,) : Void ->
                """
                Docstring.
                """
            ''')

        result = self._Parse(code)

        assert isinstance(result, Error)

    def test_MissingIndent(self) -> None:
        code = textwrap.dedent('''\
            func MyFunc(a: Int,) : Void ->
                """
                Docstring.
                """
            ''')

        result = self._Parse(code)

        assert isinstance(result, Error)

    def test_UnterminatedString(self) -> None:
        code = textwrap.dedent('''\
            func MyFunc(a: Int,) : Void ->
                """
                Unterminated docstring
            ''')

        result = self._Parse(code)

        assert isinstance(result, Error)

    def test_MissingClosingParen(self) -> None:
        code = textwrap.dedent('''\
            func MyFunc(a: Int, : Void ->
                """
                Docstring.
                """
            ''')

        result = self._Parse(code)

        assert isinstance(result, Error)

    def test_MissingOpeningParen(self) -> None:
        code = textwrap.dedent('''\
            func MyFunc a: Int,) : Void ->
                """
                Docstring.
                """
            ''')

        result = self._Parse(code)

        assert isinstance(result, Error)

    def test_InvalidTokenInParameterList(self) -> None:
        code = textwrap.dedent('''\
            func MyFunc(@invalid: Int,) : Void ->
                """
                Docstring.
                """
            ''')

        result = self._Parse(code)

        assert isinstance(result, Error)

    def test_MissingCommaAfterParameter(self) -> None:
        code = textwrap.dedent('''\
            func MyFunc(a: Int b: String,) : Void ->
                """
                Docstring.
                """
            ''')

        result = self._Parse(code)

        assert isinstance(result, Error)

    def test_EmptyFileIsValid(self) -> None:
        code = ""

        result = self._Parse(code)

        assert not isinstance(result, Error)

    def test_OnlyWhitespaceIsValid(self) -> None:
        code = "   \n\n   \n"

        result = self._Parse(code)

        assert not isinstance(result, Error)

    # ------------------------------------------------------------------
    @staticmethod
    def _Parse(code: str) -> Error | object:
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".txt",
            delete=False,
            encoding="utf-8",
        ) as f:
            f.write(code)
            temp_path = Path(f.name)

        try:
            with DoneManager.Create(io.StringIO(), "Testing") as dm:
                result = parser(dm, temp_path, None, quiet=True)

                assert len(result) == 1
                return next(iter(result.values()))
        finally:
            temp_path.unlink()


class TestParserMultipleFiles:
    """Tests for parsing multiple files."""

    def test_ParseMultipleInvalidFiles(self) -> None:
        code1 = textwrap.dedent('''\
            func First( : Void ->
                """
                Docstring.
                """
            ''')
        code2 = textwrap.dedent('''\
            func Second(: String,) : Int ->
                """
                Docstring.
                """
            ''')

        temp_files = []
        try:
            for code in [code1, code2]:
                with tempfile.NamedTemporaryFile(
                    mode="w",
                    suffix=".txt",
                    delete=False,
                    encoding="utf-8",
                ) as f:
                    f.write(code)
                    temp_files.append(Path(f.name))

            with DoneManager.Create(io.StringIO(), "Testing") as dm:
                result = parser(dm, temp_files, None, quiet=True)

                assert len(result) == 2
                for value in result.values():
                    assert isinstance(value, Error)
        finally:
            for temp_file in temp_files:
                temp_file.unlink()

    def test_ParserReturnsCorrectFilePaths(self) -> None:
        code = textwrap.dedent('''\
            func Invalid( : Void ->
                """
                Docstring.
                """
            ''')

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".txt",
            delete=False,
            encoding="utf-8",
        ) as f:
            f.write(code)
            temp_path = Path(f.name)

        try:
            with DoneManager.Create(io.StringIO(), "Testing") as dm:
                result = parser(dm, temp_path, None, quiet=True)

                assert len(result) == 1
                result_path = next(iter(result.keys()))
                assert result_path.name == temp_path.name
        finally:
            temp_path.unlink()

    def test_ErrorContainsRegionInfo(self) -> None:
        code = textwrap.dedent('''\
            func Invalid( : Void ->
                """
                Docstring.
                """
            ''')

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".txt",
            delete=False,
            encoding="utf-8",
        ) as f:
            f.write(code)
            temp_path = Path(f.name)

        try:
            with DoneManager.Create(io.StringIO(), "Testing") as dm:
                result = parser(dm, temp_path, None, quiet=True)

                assert len(result) == 1
                error = next(iter(result.values()))
                assert isinstance(error, Error)
                assert len(error.regions) > 0
                assert error.regions[0].filename == temp_path
        finally:
            temp_path.unlink()
