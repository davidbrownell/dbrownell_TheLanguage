# noqa: D100
from dataclasses import dataclass
from typing import override

from dbrownell_ParserLib.terminal_element import TerminalElement  # noqa: TC002

from dbrownell_TheLanguage.Elements.Statements.Statement import Statement


# ----------------------------------------------------------------------
@dataclass(eq=False)
class DocstringStatement(Statement):
    """A docstring statement."""

    value: TerminalElement[str]

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @override
    def _GenerateAcceptDetails(self) -> Statement._GenerateAcceptDetailsResultType:
        yield "value", self.value
