# noqa: D104
from typing import cast, TYPE_CHECKING

from dbrownell_ParserLib import (
    AntlrVisitorMixinBase,
    CreateAntlrParser,
    SignificantWhitespaceAntlrVisitorMixin,
)

from dbrownell_TheLanguage.Parser.GeneratedCode.TheLanguageLexer import TheLanguageLexer
from dbrownell_TheLanguage.Parser.GeneratedCode.TheLanguageParser import TheLanguageParser
from dbrownell_TheLanguage.Parser.GeneratedCode.TheLanguageVisitor import TheLanguageVisitor

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    import antlr4


# ----------------------------------------------------------------------
# |
# |  Private Types
# |
# ----------------------------------------------------------------------
class _Visitor(SignificantWhitespaceAntlrVisitorMixin, TheLanguageVisitor):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        filename: Path,
        on_progress_func: Callable[[int], None],
        *,
        is_included_file: bool,
    ) -> None:
        AntlrVisitorMixinBase.__init__(
            self,
            filename,
            on_progress_func,
            is_included_file=is_included_file,
        )

        SignificantWhitespaceAntlrVisitorMixin.__init__(
            self,
            TheLanguageParser.DEDENT,
            TheLanguageParser.NEWLINE,
            "newLine",
        )


# ----------------------------------------------------------------------
# |
# |  Private Functions
# |
# ----------------------------------------------------------------------
def _InitializeLexer(lexer: antlr4.Lexer) -> None:
    cast(TheLanguageLexer, lexer).CustomInit()


# ----------------------------------------------------------------------
# |
# |  Public Types
# |
# ----------------------------------------------------------------------
parser = CreateAntlrParser(
    TheLanguageLexer,
    TheLanguageParser,
    _Visitor,
    lambda parser: cast(TheLanguageParser, parser).entry_point__(),
    _InitializeLexer,
)
