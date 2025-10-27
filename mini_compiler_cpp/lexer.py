import re
from tokens import TokenKind, KEYWORDS

class Token:
    def __init__(self, kind, lexeme, value=None, line=1, col=1):
        self.kind=kind; self.lexeme=lexeme; self.value=value; self.line=line; self.col=col
    def __repr__(self):
        v=f", val={self.value}" if self.value is not None else ""
        return f"Token({self.kind.name}, '{self.lexeme}'{v}, @{self.line}:{self.col})"

sym = {
    '+':TokenKind.PLUS,'-':TokenKind.MINUS,'*':TokenKind.STAR,'/':TokenKind.SLASH,'%':TokenKind.PERCENT,
    '(':TokenKind.LPAREN,')':TokenKind.RPAREN,'{':TokenKind.LBRACE,'}':TokenKind.RBRACE,
    ',':TokenKind.COMMA,';':TokenKind.SEMI,'=':TokenKind.ASSIGN,'<':TokenKind.LT,'>':TokenKind.GT
}

def lex(src:str):
    i=0; line=1; col=1; n=len(src)
    def adv():
        nonlocal i, col
        ch=src[i]; i+=1; col+=1; return ch
    def peek(k=0):
        j=i+k
        return src[j] if j<n else '\0'
    toks=[]
    while i<n:
        ch=peek()
        if ch in ' \t': adv(); continue
        if ch=='\n': adv(); line+=1; col=1; continue
        if ch=='/' and peek(1)=='/':
            while i<n and peek()!='\n': adv()
            continue
        # numbers
        if ch.isdigit():
            start=i; start_col=col
            while peek().isdigit(): adv()
            # include first digit
            lit=src[start:i+0]
            # fix because start at peek()
            # rebuild properly
            j=start
            while j<n and src[j].isdigit(): j+=1
            lit=src[start:j]; i=j; col+= (j-start)
            toks.append(Token(TokenKind.INT, lit, int(lit), line, start_col))
            continue
        # identifiers / keywords
        if ch.isalpha() or ch=='_':
            start=i; start_col=col
            while peek().isalnum() or peek()=='_': adv()
            j=start
            while j<n and (src[j].isalnum() or src[j]=='_'): j+=1
            lexeme=src[start:j]; i=j; col+=(j-start)
            kind=KEYWORDS.get(lexeme, TokenKind.IDENT)
            toks.append(Token(kind, lexeme, None, line, start_col))
            continue
        # two-char ops
        if ch in ['=','!','<','>'] and peek(1)=='=':
            start_col=col
            a=adv(); b=adv(); lexeme=a+b
            kind={ '==':TokenKind.EQ,'!=':TokenKind.NE,'<=':TokenKind.LE,'>=':TokenKind.GE }[lexeme]
            toks.append(Token(kind, lexeme, None, line, start_col))
            continue
        # single-char
        if ch in sym:
            kind=sym[ch]; start_col=col
            adv(); toks.append(Token(kind, ch, None, line, start_col)); continue
        raise SyntaxError(f"Unknown character '{ch}' at {line}:{col}")
    toks.append(Token(TokenKind.EOF, '', None, line, col))
    return toks




