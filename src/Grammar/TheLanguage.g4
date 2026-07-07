grammar TheLanguage;

// ----------------------------------------------------------------------
tokens { INDENT, DEDENT }

@lexer::header {

from antlr_denter.DenterHelper import DenterHelper
from .TheLanguageParser import TheLanguageParser

}

@lexer::members {

def CustomInit(self):
    self._nested_pair_ctr = 0


class TheLanguageDenter(DenterHelper):
    def __init__(self, lexer, newline_token, indent_token, dedent_token):
        super().__init__(newline_token, indent_token, dedent_token, should_ignore_eof=False)

        self.lexer: TheLanguageLexer = lexer

    def pull_token(self):
        return super(TheLanguageLexer, self.lexer).nextToken()

def nextToken(self):
    if not hasattr(self, "_denter"):
        self._denter = self.__class__.TheLanguageDenter(
            self,
            TheLanguageParser.NEWLINE,
            TheLanguageParser.INDENT,
            TheLanguageParser.DEDENT,
        )

    return self._denter.next_token()
}

// ----------------------------------------------------------------------
// |
// |  Lexer Rules
// |
// ----------------------------------------------------------------------
SINGLE_LINE_COMMENT:                        '#' ~[\r\n]* -> channel(HIDDEN);
HORIZONTAL_WHITESPACE:                      [ \t]+ -> channel(HIDDEN);

// ----------------------------------------------------------------------
// Newlines nested within paired brackets brackets are safe to ignore, but newlines outside of paired
// brackets are meaningful.
NEWLINE:                                    '\r'? '\n' {self._nested_pair_ctr == 0}? [ \t]*;
NESTED_NEWLINE:                             '\r'? '\n' {self._nested_pair_ctr != 0}? [ \t]* -> channel(HIDDEN);

LINE_CONTINUATION:                          '\\' '\r'? '\n' [ \t]* -> channel(HIDDEN);

LPAREN:                                     '(' {self._nested_pair_ctr += 1};
RPAREN:                                     ')' {self._nested_pair_ctr -= 1};
LBRACK:                                     '[' {self._nested_pair_ctr += 1};
RBRACK:                                     ']' {self._nested_pair_ctr -= 1};
LBRACE:                                     '{' {self._nested_pair_ctr += 1};
RBRACE:                                     '}' {self._nested_pair_ctr -= 1};

TRIPLE_DOUBLE_QUOTE_STRING:                 UNTERMINATED_TRIPLE_DOUBLE_QUOTE_STRING '"""';
UNTERMINATED_TRIPLE_DOUBLE_QUOTE_STRING:    '"""' .*?;

IDENTIFIER:                                 ('_'* [a-zA-Z][a-zA-Z0-9_]*) | '_';

// ----------------------------------------------------------------------
// |
// |  Parser Rules
// |
// ----------------------------------------------------------------------

// ----------------------------------------------------------------------
// |  Common functionality
identifier:                                 IDENTIFIER;
triple_double_quote_string:                 TRIPLE_DOUBLE_QUOTE_STRING;

type_decorator:                             ':' identifier;

// BugBug: Support variadic parameters
parameter:                                  (identifier type_decorator) | '*';
parameter_list:                             LPAREN (parameter ',')* RPAREN;

scope_start__:                              '->' INDENT;
scope_end__:                                DEDENT;

// ----------------------------------------------------------------------
// |  Rules
entry_point__:                              NEWLINE* statement__* EOF;

statement__:                                (
                                                docstring_statement |
                                                func_statement
                                            );

docstring_statement:                        triple_double_quote_string NEWLINE;
func_statement:                             'func' identifier parameter_list type_decorator scope_start__ statement__+ scope_end__;
