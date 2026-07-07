import io
import tempfile
import textwrap

from pathlib import Path

from dbrownell_Common.Streams.DoneManager import DoneManager
from dbrownell_ParserLib.errors import Error

from dbrownell_TheLanguage.Parser import parser


# ----------------------------------------------------------------------
class TestParserInvalidInput:
    # ----------------------------------------------------------------------
    def test_MissingFunctionName(self) -> None:
        code = textwrap.dedent('''\
            func (a: Int,) : Void ->
                """
                Docstring.
                """
            ''')

        result = self._Parse(code)

        assert isinstance(result, Error)
        assert result.message == "Syntax error: extraneous input '(' expecting IDENTIFIER"
        assert result.regions[0].begin.line == 1
        assert result.regions[0].begin.column == 6
        assert result.regions[0].end.line == 1
        assert result.regions[0].end.column == 6

    # ----------------------------------------------------------------------
    def test_MissingParameterList(self) -> None:
        code = textwrap.dedent('''\
            func MyFunc : Void ->
                """
            Docstring.
            """
            ''')

        result = self._Parse(code)

        assert isinstance(result, Error)
        assert result.message == "Syntax error: mismatched input ':' expecting '('"
        assert result.regions[0].begin.line == 1
        assert result.regions[0].begin.column == 13
        assert result.regions[0].end.line == 1
        assert result.regions[0].end.column == 13

    # ----------------------------------------------------------------------
    def test_MissingReturnType(self) -> None:
        code = textwrap.dedent('''\
            func MyFunc(a: Int,) ->
                """
                Docstring.
                """
            ''')

        result = self._Parse(code)

        assert isinstance(result, Error)
        assert result.message == "Syntax error: mismatched input '->' expecting ':'"
        assert result.regions[0].begin.line == 1
        assert result.regions[0].begin.column == 22
        assert result.regions[0].end.line == 1
        assert result.regions[0].end.column == 22

    # ----------------------------------------------------------------------
    def test_MissingArrow(self) -> None:
        code = textwrap.dedent('''\
            func MyFunc(a: Int,) : Void
                """
                Docstring.
                """
            ''')

        result = self._Parse(code)

        assert isinstance(result, Error)
        assert result.message == "Syntax error: missing '->' at 'indent'"
        assert result.regions[0].begin.line == 1
        assert result.regions[0].begin.column == 28
        assert result.regions[0].end.line == 1
        assert result.regions[0].end.column == 28

    # ----------------------------------------------------------------------
    def test_MissingBody(self) -> None:
        code = textwrap.dedent("""\
            func MyFunc(a: Int,) : Void ->
            """)

        result = self._Parse(code)

        assert isinstance(result, Error)
        assert result.message == "Syntax error: mismatched input 'newLine' expecting INDENT"
        assert result.regions[0].begin.line == 2
        assert result.regions[0].begin.column == 1
        assert result.regions[0].end.line == 2
        assert result.regions[0].end.column == 1

    # ----------------------------------------------------------------------
    def test_MissingParameterType(self) -> None:
        code = textwrap.dedent('''\
            func MyFunc(a,) : Void ->
                """
                Docstring.
                """
            ''')

        result = self._Parse(code)

        assert isinstance(result, Error)
        assert result.message == "Syntax error: mismatched input ',' expecting ':'"
        assert result.regions[0].begin.line == 1
        assert result.regions[0].begin.column == 14
        assert result.regions[0].end.line == 1
        assert result.regions[0].end.column == 14

    # ----------------------------------------------------------------------
    def test_MissingParameterName(self) -> None:
        code = textwrap.dedent('''\
            func MyFunc(: Int,) : Void ->
                """
                Docstring.
                """
            ''')

        result = self._Parse(code)

        assert isinstance(result, Error)
        assert result.message == "Syntax error: extraneous input ':' expecting {'*', ')', IDENTIFIER}"
        assert result.regions[0].begin.line == 1
        assert result.regions[0].begin.column == 13
        assert result.regions[0].end.line == 1
        assert result.regions[0].end.column == 13

    # ----------------------------------------------------------------------
    def test_InvalidIdentifier(self) -> None:
        code = textwrap.dedent('''\
            func 123Invalid(a: Int,) : Void ->
                """
                Docstring.
                """
            ''')

        result = self._Parse(code)

        assert isinstance(result, Error)
        assert result.message == "Syntax error: token recognition error at: '1'"
        assert result.regions[0].begin.line == 1
        assert result.regions[0].begin.column == 6
        assert result.regions[0].end.line == 1
        assert result.regions[0].end.column == 6

    # ----------------------------------------------------------------------
    def test_MissingIndent(self) -> None:
        code = textwrap.dedent('''\
            func MyFunc(a: Int,) : Void ->
            """
            Docstring.
            """
            ''')

        result = self._Parse(code)

        assert isinstance(result, Error)
        assert result.message == "Syntax error: mismatched input '\\n' expecting INDENT"
        assert result.regions[0].begin.line == 1
        assert result.regions[0].begin.column == 31
        assert result.regions[0].end.line == 1
        assert result.regions[0].end.column == 31

    # ----------------------------------------------------------------------
    def test_UnterminatedString(self) -> None:
        code = textwrap.dedent('''\
            func MyFunc(a: Int,) : Void ->
                """
                Unterminated docstring
            ''')

        result = self._Parse(code)

        assert isinstance(result, Error)
        assert (
            result.message
            == "Syntax error: mismatched input '\"\"\"' expecting {'func', TRIPLE_DOUBLE_QUOTE_STRING}"
        )
        assert result.regions[0].begin.line == 2
        assert result.regions[0].begin.column == 5
        assert result.regions[0].end.line == 2
        assert result.regions[0].end.column == 5

    # ----------------------------------------------------------------------
    def test_MissingClosingParen(self) -> None:
        code = textwrap.dedent('''\
            func MyFunc(a: Int, : Void ->
                """
                Docstring.
                """
            ''')

        result = self._Parse(code)

        assert isinstance(result, Error)
        assert result.message == "Syntax error: extraneous input ':' expecting {'*', ')', IDENTIFIER}"
        assert result.regions[0].begin.line == 1
        assert result.regions[0].begin.column == 21
        assert result.regions[0].end.line == 1
        assert result.regions[0].end.column == 21

    # ----------------------------------------------------------------------
    def test_MissingOpeningParen(self) -> None:
        code = textwrap.dedent('''\
            func MyFunc a: Int,) : Void ->
                """
                Docstring.
                """
            ''')

        result = self._Parse(code)

        assert isinstance(result, Error)
        assert result.message == "Syntax error: missing '(' at 'a'"
        assert result.regions[0].begin.line == 1
        assert result.regions[0].begin.column == 13
        assert result.regions[0].end.line == 1
        assert result.regions[0].end.column == 13

    # ----------------------------------------------------------------------
    def test_InvalidTokenInParameterList(self) -> None:
        code = textwrap.dedent('''\
            func MyFunc(@invalid: Int,) : Void ->
                """
                Docstring.
                """
            ''')

        result = self._Parse(code)

        assert isinstance(result, Error)
        assert result.message == "Syntax error: token recognition error at: '@'"
        assert result.regions[0].begin.line == 1
        assert result.regions[0].begin.column == 13
        assert result.regions[0].end.line == 1
        assert result.regions[0].end.column == 13

    # ----------------------------------------------------------------------
    def test_MissingCommaAfterParameter(self) -> None:
        code = textwrap.dedent('''\
            func MyFunc(a: Int b: String,) : Void ->
                """
                Docstring.
                """
            ''')

        result = self._Parse(code)

        assert isinstance(result, Error)
        assert result.message == "Syntax error: missing ',' at 'b'"
        assert result.regions[0].begin.line == 1
        assert result.regions[0].begin.column == 20
        assert result.regions[0].end.line == 1
        assert result.regions[0].end.column == 20

    # ----------------------------------------------------------------------
    def test_InvalidDocstring(self) -> None:
        code = textwrap.dedent('''\
            func MyFunc(a: Int, b: String,) : Void ->
                """
              Docstring.
                """
            ''')

        result = self._Parse(code)

        assert isinstance(result, Error)
        assert (
            result.message
            == "All lines in a multiline string must be vertically aligned with the opening token."
        )
        assert result.regions[0].begin.line == 3
        assert result.regions[0].begin.column == 3
        assert result.regions[0].end.line == 3
        assert result.regions[0].end.column == 3

    # ----------------------------------------------------------------------
    def test_EmptyFileIsValid(self) -> None:
        code = ""

        result = self._Parse(code)

        assert not isinstance(result, Error)

    # ----------------------------------------------------------------------
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


# ----------------------------------------------------------------------
class TestParserMultipleFiles:
    # ----------------------------------------------------------------------
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

    # ----------------------------------------------------------------------
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

    # ----------------------------------------------------------------------
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


# ----------------------------------------------------------------------
class TestParserStandardScenarios:
    # ----------------------------------------------------------------------
    def test_SingleComment(self) -> None:
        code = "# This is a comment"

        result = self._Parse(code)

        assert not isinstance(result, Error)

    # ----------------------------------------------------------------------
    def test_MultipleComments(self) -> None:
        code = textwrap.dedent("""\
            # Comment 1
            # Comment 2
            # Comment 3""")

        result = self._Parse(code)

        assert not isinstance(result, Error)

    # ----------------------------------------------------------------------
    def test_CommentsWithBlankLines(self) -> None:
        code = textwrap.dedent("""\
            # Comment 1

            # Comment 2""")

        result = self._Parse(code)

        assert not isinstance(result, Error)

    # ----------------------------------------------------------------------
    def test_TrailingNewlineOnly(self) -> None:
        code = textwrap.dedent("""
            """)

        result = self._Parse(code)

        assert not isinstance(result, Error)

    # ----------------------------------------------------------------------
    def test_MultipleBlankLines(self) -> None:
        code = textwrap.dedent("""



            """)

        result = self._Parse(code)

        assert not isinstance(result, Error)

    # ----------------------------------------------------------------------
    def test_CommentWithTrailingNewlines(self) -> None:
        code = textwrap.dedent("""\
            # Comment


            """)

        result = self._Parse(code)

        assert not isinstance(result, Error)

    # ----------------------------------------------------------------------
    def test_MultipleCommentsWithMixedSpacing(self) -> None:
        code = textwrap.dedent("""\
            # First


            # Second
            # Third""")

        result = self._Parse(code)

        assert not isinstance(result, Error)

    # ----------------------------------------------------------------------
    def test_CommentWithSpecialCharacters(self) -> None:
        code = "# Special chars: @#$%^&*()_+-=[]{}|;':\",./<>?"

        result = self._Parse(code)

        assert not isinstance(result, Error)

    # ----------------------------------------------------------------------
    def test_CommentWithUnicode(self) -> None:
        code = "# Unicode: \u4e2d\u6587 \u65e5\u672c\u8a9e \ud55c\uad6d\uc5b4 \u03b1\u03b2\u03b3"

        result = self._Parse(code)

        assert not isinstance(result, Error)

    # ----------------------------------------------------------------------
    def test_LongComment(self) -> None:
        code = "# " + "x" * 1000

        result = self._Parse(code)

        assert not isinstance(result, Error)

    # ----------------------------------------------------------------------
    def test_CommentWithLeadingSpaces(self) -> None:
        code = "    # Indented comment"

        result = self._Parse(code)

        assert not isinstance(result, Error)

    # ----------------------------------------------------------------------
    def test_CommentWithTabs(self) -> None:
        code = "\t# Tab-indented comment"

        result = self._Parse(code)

        assert not isinstance(result, Error)

    # ----------------------------------------------------------------------
    def test_ConsistentIndentationComments(self) -> None:
        code = textwrap.dedent("""\
            # First comment
            # Second comment
            # Third comment
            # Fourth comment""")

        result = self._Parse(code)

        assert not isinstance(result, Error)

    # ----------------------------------------------------------------------
    def test_CommentFollowedByBlankLines(self) -> None:
        code = "# Comment\n\n\n\n"

        result = self._Parse(code)

        assert not isinstance(result, Error)

    # ----------------------------------------------------------------------
    def test_BlankLinesFollowedByComment(self) -> None:
        code = "\n\n\n# Comment"

        result = self._Parse(code)

        assert not isinstance(result, Error)

    # ----------------------------------------------------------------------
    def test_OnlySpaces(self) -> None:
        code = "     "

        result = self._Parse(code)

        assert not isinstance(result, Error)

    # ----------------------------------------------------------------------
    def test_OnlyTabs(self) -> None:
        code = "\t\t\t"

        result = self._Parse(code)

        assert not isinstance(result, Error)

    # ----------------------------------------------------------------------
    def test_MixedWhitespace(self) -> None:
        code = "  \t  \t  "

        result = self._Parse(code)

        assert not isinstance(result, Error)

    # ----------------------------------------------------------------------
    def test_WhitespaceWithNewlines(self) -> None:
        code = "  \n\t\n  \t\n"

        result = self._Parse(code)

        assert not isinstance(result, Error)

    # ----------------------------------------------------------------------
    def test_CarriageReturnNewline(self) -> None:
        code = "# Comment\r\n# Another"

        result = self._Parse(code)

        assert not isinstance(result, Error)

    # ----------------------------------------------------------------------
    def test_MixedLineEndings(self) -> None:
        code = "# Unix\n# Windows\r\n# Unix again\n"

        result = self._Parse(code)

        assert not isinstance(result, Error)

    # ----------------------------------------------------------------------
    def test_EmptyCommentLine(self) -> None:
        code = "#"

        result = self._Parse(code)

        assert not isinstance(result, Error)

    # ----------------------------------------------------------------------
    def test_MultipleEmptyComments(self) -> None:
        code = "#\n#\n#"

        result = self._Parse(code)

        assert not isinstance(result, Error)

    # ----------------------------------------------------------------------
    def test_CommentWithOnlySpaces(self) -> None:
        code = "#     "

        result = self._Parse(code)

        assert not isinstance(result, Error)

    # ----------------------------------------------------------------------
    def test_FuncWithDocstring(self) -> None:
        code = textwrap.dedent('''\
            func MyFunc1(a: Int,) : Void ->
                """
                Docstring.
                Line2
                    Line3
                Line4
                """


            func MyFunc2(*, b: Int,) : Void ->
                """
                Docstring.
                """


            ''')

        result = self._Parse(code)
        print(result)  # BugBug

        assert not isinstance(result, Error)

    # ----------------------------------------------------------------------
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
