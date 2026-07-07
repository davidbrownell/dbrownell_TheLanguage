# noqa: D100
from dbrownell_TheLanguage.Entities.Common.Identifier import Identifier
from dataclasses import dataclass, field
from enum import auto, Enum
from typing import cast, override

from dbrownell_ParserLib.expression import Expression as ParserLibExpression

from dbrownell_TheLanguage.Entities.Common.Identifier import Identifier
from dbrownell_TheLanguage.Entities.Common.Type import Type


# ----------------------------------------------------------------------
class ParameterType(Enum):
    """The type of a parameter."""

    Positional = auto()
    Keyword = auto()


# ----------------------------------------------------------------------
@dataclass(eq=False)
class Parameter(ParserLibExpression):
    """A parameter in TheLanguage."""

    name: Identifier
    the_type: Type
    parameter_type: ParameterType
    is_variadic: bool = field(kw_only=True, default=False)

    # ----------------------------------------------------------------------
    def _GenerateAcceptDetails(self) -> ParserLibExpression._GenerateAcceptDetailsResultType:
        yield "name", self.name
        yield "the_type", self.the_type


# ----------------------------------------------------------------------
@dataclass(eq=False)
class Parameters(ParserLibExpression):
    """A collection of parameters."""

    parameters: list[Parameter]

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @override
    def _GenerateAcceptDetails(self) -> ParserLibExpression._GenerateAcceptDetailsResultType:
        yield "parameters", cast(list[ParserLibExpression], self.parameters)
