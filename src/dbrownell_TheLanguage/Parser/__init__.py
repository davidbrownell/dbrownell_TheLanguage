# noqa: D104
from typing import cast, TYPE_CHECKING

import antlr4

from dbrownell_ParserLib.antlr.antlr_visitor_mixin import AntlrVisitorMixin
from dbrownell_ParserLib.antlr.antlr_parser import CreateAntlrParser
from dbrownell_ParserLib.errors import CreateErrorType
from dbrownell_ParserLib.multiline_strings import ExtractMultilineString
from dbrownell_ParserLib.region import Region
from dbrownell_ParserLib.terminal_element import TerminalElement

from dbrownell_TheLanguage.Entities.Common.Identifier import Identifier, IdentifierType
from dbrownell_TheLanguage.Entities.Common.Parameters import Parameter, ParameterType, Parameters
from dbrownell_TheLanguage.Entities.Common.Type import Type
from dbrownell_TheLanguage.Entities.Statements.DocstringStatement import DocstringStatement
from dbrownell_TheLanguage.Entities.Statements.FuncStatement import FuncStatement
from dbrownell_TheLanguage.Entities.Statements.Statement import Statement
from dbrownell_TheLanguage.Parser.GeneratedCode.TheLanguageLexer import TheLanguageLexer
from dbrownell_TheLanguage.Parser.GeneratedCode.TheLanguageParser import TheLanguageParser
from dbrownell_TheLanguage.Parser.GeneratedCode.TheLanguageVisitor import TheLanguageVisitor

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path


# ----------------------------------------------------------------------
# |
# |  Errors
# |
# ----------------------------------------------------------------------
TypeIdentifierExpectedError = CreateErrorType("A type identifier was expected.")
DuplicateKeywordParameterError = CreateErrorType(
    "The keyword parameter delimiter was already provided at '{prev_region}'.", prev_region=Region
)


# ----------------------------------------------------------------------
# |
# |  Private Types
# |
# ----------------------------------------------------------------------
class _Visitor(AntlrVisitorMixin, TheLanguageVisitor):
    # ----------------------------------------------------------------------
    def visitIdentifier(
        self,
        ctx: TheLanguageParser.IdentifierContext,
    ) -> None:
        value = ctx.getText()

        # Calculate the identifier type
        identifier_type = IdentifierType.Variable

        for c in value:
            if c == "_":
                continue

            if c.isupper():
                identifier_type = IdentifierType.Type
            elif c.islower():
                identifier_type = IdentifierType.Variable
            else:
                assert False, c  # noqa: B011, PT015

            break

        self._stack.append(Identifier(self.CreateRegion(ctx), value, identifier_type))

    # ----------------------------------------------------------------------
    def visitTriple_double_quote_string(
        self,
        ctx: TheLanguageParser.Triple_double_quote_stringContext,
    ) -> None:
        assert ctx.children is not None
        assert len(ctx.children) == 1, ctx.children
        child = ctx.children[0]

        region = self.CreateRegion(child)

        content = ExtractMultilineString(
            child.getText(),
            region,
            '"""',
            '"""',
            tab_size=4,
        )

        # TODO: Docstrings are only valid under certain conditions

        self._stack.append(TerminalElement[str](region, content))

    # ----------------------------------------------------------------------
    def visitType_decorator(
        self,
        ctx: TheLanguageParser.Type_decoratorContext,
    ) -> None:
        assert ctx.children is not None and len(ctx.children) == 2, ctx.children

        children = self.GetChildren(ctx)
        assert len(children) == 1, children
        identifier = cast(Identifier, children[0])

        region = self.CreateRegion(ctx)

        if identifier.the_type != IdentifierType.Type:
            raise TypeIdentifierExpectedError.CreateAsException(region)

        self._stack.append(Type(region, identifier))

    # ----------------------------------------------------------------------
    def visitParameter(
        self,
        ctx: TheLanguageParser.ParameterContext,
    ) -> None:
        assert ctx.children is not None

        region = self.CreateRegion(ctx)

        if len(ctx.children) == 1 and isinstance(ctx.children[0], antlr4.TerminalNode):
            assert ctx.getText() == "*", ctx.getText()
            self._stack.append(("*", region))

            return

        # Don't create the Parameter yet, as we don't have enough information to determine if the
        # parameter is a positional or keyword parameter.
        self._stack.append(region)

        self.visitChildren(ctx)

    # ----------------------------------------------------------------------
    def visitParameter_list(
        self,
        ctx: TheLanguageParser.Parameter_listContext,
    ) -> None:
        children = cast(list[Parameter], self.GetChildren(ctx))

        parameters: list[Parameter] = []
        keyword_delimiter_region: Region | None = None

        child_index = 0
        while child_index < len(children):
            child = children[child_index]
            child_index += 1

            # Are we looking at the keyword delimiter?
            if isinstance(child, tuple):
                assert len(child) == 2, child
                assert isinstance(child[0], str) and child[0] == "*", child[0]
                assert isinstance(child[1], Region), child[1]
                region = child[1]

                if keyword_delimiter_region is not None:
                    raise DuplicateKeywordParameterError.CreateAsException(region, keyword_delimiter_region)

                # BugBug: It's an error if there aren't any parameters following this value

                keyword_delimiter_region = region
                continue

            # If here, we are looking at a standard parameter definition. There will be two additional children on the stack:
            # 1) the identifier and 2) the type.
            assert child_index + 2 <= len(children), (child_index, len(children))

            assert isinstance(child, Region), child
            assert isinstance(children[child_index], Identifier), children[child_index]
            assert isinstance(children[child_index + 1], Type), children[child_index + 1]

            region = child
            identifier = cast(Identifier, children[child_index])
            the_type = cast(Type, children[child_index + 1])

            child_index += 2

            # BugBug: Ensure that the identifier is a variable identifier

            parameters.append(
                Parameter(
                    region,
                    identifier,
                    the_type,
                    (
                        ParameterType.Keyword
                        if keyword_delimiter_region is not None
                        else ParameterType.Positional
                    ),
                    is_variadic=False,  # TODO: Support variadic parameters
                ),
            )

        self._stack.append(Parameters(self.CreateRegion(ctx), parameters))

    # ----------------------------------------------------------------------
    def visitDocstring_statement(
        self,
        ctx: TheLanguageParser.Docstring_statementContext,
    ) -> None:
        children = self.GetChildren(ctx)
        assert len(children) == 1, children
        assert isinstance(children[0], TerminalElement), children[0]

        self._stack.append(DocstringStatement(self.CreateRegion(ctx), children[0]))

    # ----------------------------------------------------------------------
    def visitFunc_statement(
        self,
        ctx: TheLanguageParser.Func_statementContext,
    ) -> None:
        children = self.GetChildren(ctx)
        assert len(children) >= 4, children

        assert isinstance(children[0], Identifier), children[0]
        assert isinstance(children[1], Parameters), children[1]
        assert isinstance(children[2], Type), children[2]
        assert all(isinstance(child, Statement) for child in children[3:]), children[3:]

        # BugBug: Look for special function names
        # BugBug: Ensure identifier is a function name
        # BugBug: Extract docstring (if any), ensure that it is the first statement, and pass it as to FuncStatement.

        self._stack.append(
            FuncStatement(
                self.CreateRegion(ctx),
                children[0],
                children[1],
                children[2],
                cast(list[Statement], children[3:]),
            ),
        )


# ----------------------------------------------------------------------
# |
# |  Private Functions
# |
# ----------------------------------------------------------------------
def _InitializeLexer(lexer: antlr4.Lexer) -> None:
    cast(TheLanguageLexer, lexer).CustomInit()


# ----------------------------------------------------------------------
# |
# |  Public Types
# |
# ----------------------------------------------------------------------
parser = CreateAntlrParser(
    TheLanguageLexer,
    TheLanguageParser,
    _Visitor,
    lambda parser: cast(TheLanguageParser, parser).entry_point__(),
    _InitializeLexer,
)
