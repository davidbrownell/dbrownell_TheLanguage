"""Contains functionality necessary to represent a function statement."""

from dataclasses import dataclass
from enum import auto, Enum
from typing import override

from dbrownell_ParserLib.terminal_expression import TerminalExpression  # noqa: TC002

from dbrownell_TheLanguage.Entities.Common.Parameters import Parameters
from dbrownell_TheLanguage.Entities.Common.Type import Type
from dbrownell_TheLanguage.Entities.Statements.Statement import Statement


# ----------------------------------------------------------------------
class SpecialFunctionType(Enum):
    """Special functions that customize an object's behavior."""

    Constructor = auto()
    Add = auto()

    # TODO: More here


# ----------------------------------------------------------------------
@dataclass(eq=False)
class FuncStatement(Statement):
    """A function."""

    name: TerminalExpression[str | SpecialFunctionType]
    parameters: Parameters
    return_type: Type | None
    statements: list[Statement]

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @override
    def _GenerateAcceptDetails(self) -> Statement._GenerateAcceptDetailsResultType:
        yield "name", self.name
        yield "parameters", self.parameters
        yield "return_type", self.return_type
        yield "docstring", self.docstring

    # ----------------------------------------------------------------------
    @override
    def _GetAcceptChildren(self) -> Statement._GetAcceptChildrenResultType:
        return "statements", self.statements
