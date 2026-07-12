# noqa: D100
from dataclasses import dataclass, field
from enum import auto, Enum
from typing import cast, override

from dbrownell_ParserLib.element import Element

from dbrownell_TheLanguage.Elements.Common.Identifier import Identifier
from dbrownell_TheLanguage.Elements.Common.Type import Type


# ----------------------------------------------------------------------
class ParameterType(Enum):
    """The type of a parameter."""

    Positional = auto()
    Keyword = auto()


# ----------------------------------------------------------------------
@dataclass(eq=False)
class Parameter(Element):
    """A parameter in TheLanguage."""

    name: Identifier
    the_type: Type
    parameter_type: ParameterType
    is_variadic: bool = field(kw_only=True, default=False)

    # ----------------------------------------------------------------------
    def _GenerateAcceptDetails(self) -> Element._GenerateAcceptDetailsResultType:
        yield "name", self.name
        yield "the_type", self.the_type


# ----------------------------------------------------------------------
@dataclass(eq=False)
class Parameters(Element):
    """A collection of parameters."""

    parameters: list[Parameter]

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @override
    def _GenerateAcceptDetails(self) -> Element._GenerateAcceptDetailsResultType:
        yield "parameters", cast(list[Element], self.parameters)
