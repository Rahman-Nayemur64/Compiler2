from ast_nodes import *

class SemaError(Exception): pass

class Scope:
    def __init__(self, parent=None): self.parent=parent; self.vars=set()
    def declare(self, name):
        if name in self.vars: raise SemaError(f"Variable '{name}' redeclared")
        self.vars.add(name)
    def has(self,name):
        s=self
        while s:
            if name in s.vars: return True
            s=s.parent
        return False

class Sema:
    def __init__(self, ast): self.ast=ast; self.funcs={}
    def run(self):
        # collect funcs
        for f in self.ast.funcs:
            if f.name in self.funcs: raise SemaError(f"Function '{f.name}' redeclared")
            self.funcs[f.name]=f
        if 'main' not in self.funcs: raise SemaError("Missing entry function 'main'")
        for f in self.ast.funcs:
            self._check_func(f)

    def _check_func(self, f:Func):
        scope=Scope()
        for p in f.params:
            scope.declare(p.name)
        must_return=(f.name!='print')
        has_ret=self._check_block(f.body, scope)
        if f.name=='main' and not has_ret:
            raise SemaError("non-void function must return a value")

    def _check_block(self, blk:Block, scope:Scope):
        local=Scope(scope)
        has_ret=False
        for s in blk.stmts:
            if isinstance(s, VarDecl):
                local.declare(s.name)
                if s.init: self._check_expr(s.init, local)
            elif isinstance(s, Assign):
                if not local.has(s.name): raise SemaError(f"Undeclared variable '{s.name}'")
                self._check_expr(s.expr, local)
            elif isinstance(s, If):
                self._check_expr(s.cond, local)
                r1=self._check_block(s.then, local)
                r2=False
                if s.els: r2=self._check_block(s.els, local)
                has_ret = has_ret or (r1 and r2)
            elif isinstance(s, While):
                self._check_expr(s.cond, local)
                _=self._check_block(s.body, local)
            elif isinstance(s, Return):
                self._check_expr(s.expr, local)
                has_ret=True
            elif isinstance(s, Print):
                self._check_expr(s.expr, local)
            elif isinstance(s, Call):
                if s.name not in self.funcs and s.name!='print':
                    raise SemaError(f"Call to unknown function '{s.name}'")
                for a in s.args: self._check_expr(a, local)
            else:
                raise SemaError(f"Unknown statement {type(s)}")
        return has_ret

    def _check_expr(self, e, scope:Scope):
        if isinstance(e, (Int,)): return
        if isinstance(e, Var):
            if not scope.has(e.name): raise SemaError(f"Undeclared variable '{e.name}'")
        elif isinstance(e, BinOp):
            self._check_expr(e.left, scope); self._check_expr(e.right, scope)
        elif isinstance(e, Unary):
            self._check_expr(e.expr, scope)
        elif isinstance(e, Call):
            if e.name not in self.funcs and e.name!='print':
                raise SemaError(f"Call to unknown function '{e.name}'")
            for a in e.args: self._check_expr(a, scope)
        else:
            raise SemaError(f"Unknown expr {type(e)}")







