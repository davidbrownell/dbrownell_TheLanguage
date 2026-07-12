# noqa: D100
from dataclasses import dataclass

from dbrownell_ParserLib.element import Element


# ----------------------------------------------------------------------
@dataclass(eq=False)
class Statement(Element):
    """Abstract base class for all statements in TheLanguage."""
