from ast_nodes import *
from tokens import TokenKind

class TAC:
    def __init__(self): self.lines=[]; self.tmp=0; self.lbl=0
    def newt(self): self.tmp+=1; return f"t{self.tmp}"
    def newl(self, base='L'): self.lbl+=1; return f"{base}{self.lbl}"
    def emit(self, s): self.lines.append(s)

class Codegen:
    def __init__(self, ast): self.ast=ast; self.tac=TAC()
    def run(self):
        for f in self.ast.funcs:
            self.tac.emit(f"func {f.name}:")
            self._block(f.body)
            if f.name!='main': self.tac.emit("return")
            self.tac.emit("endfunc\n")
        return self.tac.lines

    def _block(self, blk:Block):
        for s in blk.stmts:
            if isinstance(s, VarDecl):
                if s.init:
                    v=self._expr(s.init)
                    self.tac.emit(f"{s.name} = {v}")
                else:
                    self.tac.emit(f"{s.name} = 0")
            elif isinstance(s, Assign):
                v=self._expr(s.expr)
                self.tac.emit(f"{s.name} = {v}")
            elif isinstance(s, If):
                cond=self._expr(s.cond)
                l_then=self.tac.newl('L_then_'); l_end=self.tac.newl('L_end_')
                if s.els:
                    l_else=self.tac.newl('L_else_')
                    self.tac.emit(f"if {cond} goto {l_then}")
                    self.tac.emit(f"goto {l_else}")
                    self.tac.emit(f"{l_then}:")
                    self._block(s.then)
                    self.tac.emit(f"goto {l_end}")
                    self.tac.emit(f"{l_else}:")
                    self._block(s.els)
                    self.tac.emit(f"{l_end}:")
                else:
                    self.tac.emit(f"if {cond} goto {l_then}")
                    self.tac.emit(f"goto {l_end}")
                    self.tac.emit(f"{l_then}:")
                    self._block(s.then)
                    self.tac.emit(f"{l_end}:")
            elif isinstance(s, While):
                l_cond=self.tac.newl('L_cond_'); l_body=self.tac.newl('L_body_'); l_end=self.tac.newl('L_end_')
                self.tac.emit(f"{l_cond}:")
                c=self._expr(s.cond)
                self.tac.emit(f"if {c} goto {l_body}")
                self.tac.emit(f"goto {l_end}")
                self.tac.emit(f"{l_body}:")
                self._block(s.body)
                self.tac.emit(f"goto {l_cond}")
                self.tac.emit(f"{l_end}:")
            elif isinstance(s, Return):
                v=self._expr(s.expr)
                self.tac.emit(f"return {v}")
            elif isinstance(s, Print):
                v=self._expr(s.expr)
                self.tac.emit(f"param {v}")
                self.tac.emit(f"call print, 1")
            elif isinstance(s, Call):
                args=[self._expr(a) for a in s.args]
                for a in args: self.tac.emit(f"param {a}")
                self.tac.emit(f"call {s.name}, {len(args)}")
            else:
                raise RuntimeError(f"unknown stmt {type(s)}")

    def _expr(self, e):
        if isinstance(e, Int): return str(e.value)
        if isinstance(e, Var): return e.name
        if isinstance(e, Unary) and e.op=='NEG':
            v=self._expr(e.expr); t=self.tac.newt(); self.tac.emit(f"{t} = 0 - {v}"); return t
        if isinstance(e, BinOp):
            a=self._expr(e.left); b=self._expr(e.right); t=self.tac.newt()
            opmap={
                TokenKind.PLUS:'+ ', TokenKind.MINUS:'- ', TokenKind.STAR:'* ', TokenKind.SLASH:'/ ', TokenKind.PERCENT:'% ',
                TokenKind.LT:'< ', TokenKind.LE:'<= ', TokenKind.GT:'> ', TokenKind.GE:'>= ', TokenKind.EQ:'== ', TokenKind.NE:'!= ',
            }
            op=opmap[e.op].strip()
            self.tac.emit(f"{t} = {a} {op} {b}")
            return t
        if isinstance(e, Call):
            args=[self._expr(a) for a in e.args]
            for a in args: self.tac.emit(f"param {a}")
            t=self.tac.newt(); self.tac.emit(f"{t} = call {e.name}, {len(args)}")
            return t
        raise RuntimeError(f"unknown expr {type(e)}")











