# noqa: D100
from dataclasses import dataclass
from enum import auto, Enum

from dbrownell_ParserLib.terminal_element import TerminalElement


# ----------------------------------------------------------------------
class IdentifierType(Enum):
    """The type of an identifier."""

    Variable = auto()
    Type = auto()


# ----------------------------------------------------------------------
@dataclass(eq=False)
class Identifier(TerminalElement[str]):
    """An identifier in TheLanguage."""

    the_type: IdentifierType
