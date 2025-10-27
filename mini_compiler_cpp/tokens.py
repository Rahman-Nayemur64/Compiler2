from enum import Enum, auto

class TokenKind(Enum):
    # single-char
    PLUS=auto(); MINUS=auto(); STAR=auto(); SLASH=auto(); PERCENT=auto()
    LPAREN=auto(); RPAREN=auto(); LBRACE=auto(); RBRACE=auto()
    COMMA=auto(); SEMI=auto(); ASSIGN=auto()
    # comparison
    LT=auto(); LE=auto(); GT=auto(); GE=auto(); EQ=auto(); NE=auto()
    # literals & id
    INT=auto(); IDENT=auto()
    # keywords
    KW_INT=auto(); KW_FUNC=auto(); KW_RETURN=auto(); KW_IF=auto(); KW_ELSE=auto(); KW_WHILE=auto();
    KW_PRINT=auto()
    # misc
    EOF=auto()

KEYWORDS = {
    'int': TokenKind.KW_INT,
    'func': TokenKind.KW_FUNC,
    'return': TokenKind.KW_RETURN,
    'if': TokenKind.KW_IF,
    'else': TokenKind.KW_ELSE,
    'while': TokenKind.KW_WHILE,
    'print': TokenKind.KW_PRINT,
}









