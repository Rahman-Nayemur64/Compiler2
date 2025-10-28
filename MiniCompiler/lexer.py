import re

TOKEN_SPECIFICATION = [
    ('NUMBER',   r'\d+'),
    ('RELOP',    r'==|!=|<=|>=|<|>'),
    ('ASSIGN',   r'='),
    ('END',      r';'),
    ('COMMA',    r','),
    ('LBRACE',   r'\{'),
    ('RBRACE',   r'\}'),
    ('LPAREN',   r'\('),
    ('RPAREN',   r'\)'),
    ('ID',       r'[A-Za-z_][A-Za-z0-9_]*'),
    ('OP',       r'[+\-*/]'),
    ('NEWLINE',  r'\n'),
    ('SKIP',     r'[ \t\r]+'),
    ('MISMATCH', r'.')
]
MASTER_RE = re.compile('|'.join(f'(?P<{name}>{pat})' for name, pat in TOKEN_SPECIFICATION))

def tokenize(code):
    tokens = []  # (KIND, LEXEME, LINE, COL)
    line = 1
    col = 1
    idx = 0
    n = len(code)
    while idx < n:
        m = MASTER_RE.match(code, idx)
        if not m:
            raise RuntimeError(f'Unexpected character at {line}:{col}')
        kind = m.lastgroup
        text = m.group()
        idx = m.end()
        if kind == 'NEWLINE':
            line += 1
            col = 1
            continue
        elif kind == 'SKIP':
            col += len(text)
            continue
        elif kind == 'MISMATCH':
            raise RuntimeError(f"Unexpected character: {text!r} at {line}:{col}")
        else:
            tokens.append((kind, text, line, col))
            col += len(text)
    return tokens