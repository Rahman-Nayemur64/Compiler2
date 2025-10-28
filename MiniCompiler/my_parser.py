class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else ('EOF', None, 0, 0)

    def advance(self):
        tok = self.peek()
        self.pos += 1
        return tok

    def match(self, kind, lexeme=None):
        k, v, *_ = self.peek()
        if k == kind and (lexeme is None or v == lexeme):
            return True
        return False

    def expect(self, kind, lexeme=None):
        if not self.match(kind, lexeme):
            k, v, ln, col = self.peek()
            want = f"{kind}{' '+lexeme if lexeme else ''}"
            got = f"{k} {v!r} at {ln}:{col}"
            raise SyntaxError(f"Expected {want}, got {got}")
        return self.advance()

    def parse(self):
        items = []
        while self.peek()[0] != 'EOF':
            if self.match('ID', 'func'):
                items.append(self.func_def())
            else:
                items.append(self.statement())
        return ('PROGRAM', items)

    # func id ( [id (, id)* ] ) block
    def func_def(self):
        self.expect('ID', 'func')
        _, name, *_ = self.expect('ID')
        self.expect('LPAREN')
        params = []
        if not self.match('RPAREN'):
            while True:
                _, p, *_ = self.expect('ID')
                params.append(p)
                if self.match('COMMA'):
                    self.advance()
                    continue
                break
        self.expect('RPAREN')
        body = self.block()
        return ('FUNCDEF', name, params, body)

    def block(self):
        if self.match('LBRACE'):
            self.advance()
            stmts = []
            while not self.match('RBRACE'):
                stmts.append(self.statement())
            self.expect('RBRACE')
            return ('BLOCK', stmts)
        # single statement as block
        stmt = self.statement()
        return ('BLOCK', [stmt])

    def statement(self):
        tok_type, tok_val, *_ = self.peek()

        # return statement
        if tok_type == 'ID' and tok_val == 'return':
            self.advance()
            # allow optional expression: 'return;' -> ret 0
            if self.match('END'):
                self.advance()
                return ('RETURN', None)
            expr = self.expr()
            if self.match('END'):
                self.advance()
            return ('RETURN', expr)

        # if-statement
        if tok_type == 'ID' and tok_val == 'if':
            self.advance()
            self.expect('LPAREN')
            cond = self.expr()
            self.expect('RPAREN')
            then_stmt = self.statement()
            else_stmt = None
            if self.match('ID', 'else'):
                self.advance()
                else_stmt = self.statement()
            return ('IF', cond, then_stmt, else_stmt)

        # while-statement
        if tok_type == 'ID' and tok_val == 'while':
            self.advance()
            self.expect('LPAREN')
            cond = self.expr()
            self.expect('RPAREN')
            body = self.statement()
            return ('WHILE', cond, body)

        # block
        if tok_type == 'LBRACE':
            return self.block()

        # assignment or call statement
        if tok_type == 'ID':
            # lookahead for call vs assign
            _, name, *_ = self.advance()
            if self.match('LPAREN'):
                # call statement
                self.advance()
                args = []
                if not self.match('RPAREN'):
                    while True:
                        args.append(self.expr())
                        if self.match('COMMA'):
                            self.advance()
                            continue
                        break
                self.expect('RPAREN')
                if self.match('END'):
                    self.advance()
                return ('CALL', name, args)
            # assignment
            if self.match('ASSIGN'):
                self.advance()
                expr = self.expr()
                if self.match('END'):
                    self.advance()
                return ('ASSIGN', name, expr)
            raise SyntaxError('Invalid statement starting with ID')

        raise SyntaxError('Invalid statement')

    def expr(self):
        node = self.term()
        while self.match('OP') and self.peek()[1] in ('+', '-'):
            _, op, *_ = self.advance()
            right = self.term()
            node = ('BIN_OP', op, node, right)
        if self.match('RELOP'):
            _, op, *_ = self.advance()
            right = self.expr()
            node = ('BIN_OP', op, node, right)
        return node

    def term(self):
        node = self.factor()
        while self.match('OP') and self.peek()[1] in ('*', '/'):
            _, op, *_ = self.advance()
            right = self.factor()
            node = ('BIN_OP', op, node, right)
        return node

    def factor(self):
        tok = self.advance()
        kind, val = tok[0], tok[1]
        if kind == 'NUMBER':
            return ('NUM', int(val))
        if kind == 'ID':
            # function call as expression: id(expr, ...)
            if self.match('LPAREN'):
                self.advance()
                args = []
                if not self.match('RPAREN'):
                    while True:
                        args.append(self.expr())
                        if self.match('COMMA'):
                            self.advance()
                            continue
                        break
                self.expect('RPAREN')
                return ('CALL_EXPR', val, args)
            return ('VAR', val)
        if kind == 'LPAREN':
            e = self.expr()
            self.expect('RPAREN')
            return e
        raise SyntaxError('Invalid factor')