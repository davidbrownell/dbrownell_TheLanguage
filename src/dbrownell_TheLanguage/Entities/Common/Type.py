# noqa: D100
from dataclasses import dataclass
from typing import override

from dbrownell_ParserLib.expression import Expression as ParserLibExpression
from dbrownell_ParserLib.terminal_expression import TerminalExpression  # noqa: TC002


# ----------------------------------------------------------------------
@dataclass(eq=False)
class Type(ParserLibExpression):
    """A type in TheLanguage."""

    the_type: TerminalExpression[str]

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @override
    def _GenerateAcceptDetails(self) -> ParserLibExpression._GenerateAcceptDetailsResultType:
        yield "the_type", self.the_type
