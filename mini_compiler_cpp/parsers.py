from tokens import TokenKind
from ast_nodes import *

class Parser:
    def __init__(self, tokens):
        self.toks=tokens; self.i=0
    def peek(self): return self.toks[self.i]
    def at(self,k): return self.toks[self.i].kind==k
    def eat(self,k):
        t=self.peek()
        if t.kind!=k:
            raise SyntaxError(f"Expected {k.name} got {t.kind.name} at {t.line}:{t.col}")
        self.i+=1; return t

    def parse(self):
        funcs=[]
        while not self.at(TokenKind.EOF):
            funcs.append(self.func())
        return Program(funcs)

    def func(self):
        # func name '(' params ')' '{' block '}'
        self.eat(TokenKind.KW_FUNC)
        name=self.eat(TokenKind.IDENT).lexeme
        self.eat(TokenKind.LPAREN)
        params=[]
        if not self.at(TokenKind.RPAREN):
            params.append(Param(self.eat(TokenKind.IDENT).lexeme))
            while self.at(TokenKind.COMMA):
                self.eat(TokenKind.COMMA)
                params.append(Param(self.eat(TokenKind.IDENT).lexeme))
        self.eat(TokenKind.RPAREN)
        blk=self.block()
        return Func(name, params, blk)

    def block(self):
        self.eat(TokenKind.LBRACE)
        stmts=[]
        while not self.at(TokenKind.RBRACE):
            stmts.append(self.stmt())
        self.eat(TokenKind.RBRACE)
        return Block(stmts)

    def stmt(self):
        t=self.peek()
        if t.kind==TokenKind.KW_INT:
            self.eat(TokenKind.KW_INT)
            name=self.eat(TokenKind.IDENT).lexeme
            init=None
            if self.at(TokenKind.ASSIGN):
                self.eat(TokenKind.ASSIGN)
                init=self.expr()
            self.eat(TokenKind.SEMI); return VarDecl(name, init)
        if t.kind==TokenKind.IDENT and self._next_is_assign():
            name=self.eat(TokenKind.IDENT).lexeme
            self.eat(TokenKind.ASSIGN)
            e=self.expr(); self.eat(TokenKind.SEMI); return Assign(name,e)
        if t.kind==TokenKind.KW_IF:
            self.eat(TokenKind.KW_IF); self.eat(TokenKind.LPAREN); c=self.expr(); self.eat(TokenKind.RPAREN)
            th=self.block(); el=None
            if self.at(TokenKind.KW_ELSE):
                self.eat(TokenKind.KW_ELSE); el=self.block()
            return If(c,th,el)
        if t.kind==TokenKind.KW_WHILE:
            self.eat(TokenKind.KW_WHILE); self.eat(TokenKind.LPAREN); c=self.expr(); self.eat(TokenKind.RPAREN)
            return While(c,self.block())
        if t.kind==TokenKind.KW_RETURN:
            self.eat(TokenKind.KW_RETURN); e=self.expr(); self.eat(TokenKind.SEMI); return Return(e)
        if t.kind==TokenKind.KW_PRINT:
            self.eat(TokenKind.KW_PRINT); self.eat(TokenKind.LPAREN); e=self.expr(); self.eat(TokenKind.RPAREN); self.eat(TokenKind.SEMI); return Print(e)
        # expression as statement: call
        if t.kind==TokenKind.IDENT and self._next_is(TokenKind.LPAREN):
            name=self.eat(TokenKind.IDENT).lexeme
            args=self.arglist(); self.eat(TokenKind.SEMI)
            return Call(name,args)
        raise SyntaxError(f"Unexpected token {t.kind.name} at {t.line}:{t.col}")

    def _next_is_assign(self):
        return self.toks[self.i+1].kind==TokenKind.ASSIGN
    def _next_is(self,k):
        return self.toks[self.i+1].kind==k

    def arglist(self):
        self.eat(TokenKind.LPAREN)
        args=[]
        if not self.at(TokenKind.RPAREN):
            args.append(self.expr())
            while self.at(TokenKind.COMMA):
                self.eat(TokenKind.COMMA); args.append(self.expr())
        self.eat(TokenKind.RPAREN)
        return args

    # Pratt precedence
    def expr(self): return self._equality()
    def _equality(self):
        node=self._rel()
        while self.at(TokenKind.EQ) or self.at(TokenKind.NE):
            op=self.eat(self.peek().kind).kind
            node=BinOp(op,node,self._rel())
        return node
    def _rel(self):
        node=self._term()
        while self.at(TokenKind.LT) or self.at(TokenKind.LE) or self.at(TokenKind.GT) or self.at(TokenKind.GE):
            op=self.eat(self.peek().kind).kind
            node=BinOp(op,node,self._term())
        return node
    def _term(self):
        node=self._factor()
        while self.at(TokenKind.PLUS) or self.at(TokenKind.MINUS):
            op=self.eat(self.peek().kind).kind
            node=BinOp(op,node,self._factor())
        return node
    def _factor(self):
        node=self._unary()
        while self.at(TokenKind.STAR) or self.at(TokenKind.SLASH) or self.at(TokenKind.PERCENT):
            op=self.eat(self.peek().kind).kind
            node=BinOp(op,node,self._unary())
        return node
    def _unary(self):
        if self.at(TokenKind.MINUS):
            self.eat(TokenKind.MINUS); return Unary('NEG', self._unary())
        return self._primary()
    def _primary(self):
        t=self.peek()
        if t.kind==TokenKind.INT: self.eat(TokenKind.INT); return Int(t.value)
        if t.kind==TokenKind.IDENT:
            # could be call or var
            if self._next_is(TokenKind.LPAREN):
                name=self.eat(TokenKind.IDENT).lexeme
                args=self.arglist(); return Call(name,args)
            name=self.eat(TokenKind.IDENT).lexeme; return Var(name)
        if t.kind==TokenKind.LPAREN:
            self.eat(TokenKind.LPAREN); e=self.expr(); self.eat(TokenKind.RPAREN); return e
        raise SyntaxError(f"Unexpected primary {t.kind.name} at {t.line}:{t.col}")













