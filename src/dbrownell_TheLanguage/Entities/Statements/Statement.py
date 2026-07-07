# noqa: D100
from dataclasses import dataclass

from dbrownell_ParserLib.expression import Expression as ParserLibExpression


# ----------------------------------------------------------------------
@dataclass(eq=False)
class Statement(ParserLibExpression):
    """Abstract base class for all statements in TheLanguage."""
