class Node: pass
class Program(Node):
    def __init__(self, funcs): self.funcs=funcs
class Func(Node):
    def __init__(self, name, params, body): self.name=name; self.params=params; self.body=body
class Param(Node):
    def __init__(self, name): self.name=name
class Block(Node):
    def __init__(self, stmts): self.stmts=stmts
class VarDecl(Node):
    def __init__(self, name, init): self.name=name; self.init=init
class Assign(Node):
    def __init__(self, name, expr): self.name=name; self.expr=expr
class If(Node):
    def __init__(self, cond, then, els): self.cond=cond; self.then=then; self.els=els
class While(Node):
    def __init__(self, cond, body): self.cond=cond; self.body=body
class Return(Node):
    def __init__(self, expr): self.expr=expr
class Print(Node):
    def __init__(self, expr): self.expr=expr
class Call(Node):
    def __init__(self, name, args): self.name=name; self.args=args
# expressions
class Int(Node):
    def __init__(self, value): self.value=value
class Var(Node):
    def __init__(self, name): self.name=name
class BinOp(Node):
    def __init__(self, op, left, right): self.op=op; self.left=left; self.right=right
class Unary(Node):
    def __init__(self, op, expr): self.op=op; self.expr=expr





