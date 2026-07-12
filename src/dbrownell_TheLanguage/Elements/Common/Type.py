# noqa: D100
from dataclasses import dataclass
from typing import override

from dbrownell_ParserLib.element import Element
from dbrownell_ParserLib.terminal_element import TerminalElement  # noqa: TC002


# ----------------------------------------------------------------------
@dataclass(eq=False)
class Type(Element):
    """A type in TheLanguage."""

    the_type: TerminalElement[str]

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @override
    def _GenerateAcceptDetails(self) -> Element._GenerateAcceptDetailsResultType:
        yield "the_type", self.the_type
