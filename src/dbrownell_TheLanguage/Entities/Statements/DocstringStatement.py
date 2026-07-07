# noqa: D100
from dataclasses import dataclass
from typing import override

from dbrownell_ParserLib.terminal_expression import TerminalExpression  # noqa: TC002

from dbrownell_TheLanguage.Entities.Statements.Statement import Statement


# ----------------------------------------------------------------------
@dataclass(eq=False)
class DocstringStatement(Statement):
    """A docstring statement."""

    value: TerminalExpression[str]

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @override
    def _GenerateAcceptDetails(self) -> Statement._GenerateAcceptDetailsResultType:
        yield "value", self.value
