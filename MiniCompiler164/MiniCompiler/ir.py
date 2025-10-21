from typing import List, Tuple, Union

Instr = Tuple
Operand = Union[int, str]

class IRBuilder:
    def __init__(self):
        self.code: List[Instr] = []
        self.temp_count = 0
        self.label_count = 0

    def new_temp(self) -> str:
        t = f"t{self.temp_count}"
        self.temp_count += 1
        return t

    def new_label(self, base: str = "L") -> str:
        lbl = f"{base}{self.label_count}"
        self.label_count += 1
        return lbl

    def emit(self, instr: Instr):
        self.code.append(instr)

    # Expressions return an operand
    def emit_expr(self, node) -> Operand:
        tag = node[0]
        if tag == 'NUM':
            return node[1]
        if tag == 'VAR':
            return node[1]
        if tag == 'BIN_OP':
            op = node[1]
            a = self.emit_expr(node[2])
            b = self.emit_expr(node[3])
            dst = self.new_temp()
            self.emit(('BIN', dst, op, a, b))
            return dst
        if tag == 'CALL_EXPR':
            fname = node[1]
            args = [self.emit_expr(a) for a in node[2]]
            dst = self.new_temp()
            self.emit(('CALL', dst, fname, args))
            return dst
        raise ValueError(f"Unsupported expr: {node}")

    def emit_block(self, block_node):
        assert block_node[0] == 'BLOCK'
        for s in block_node[1]:
            self.emit_stmt(s)

    def emit_stmt(self, node):
        tag = node[0]
        if tag == 'ASSIGN':
            dst = node[1]
            rhs = self.emit_expr(node[2])
            self.emit(('MOV', dst, rhs))
            return
        if tag == 'CALL':
            # call used as a statement; result ignored
            fname = node[1]
            args = [self.emit_expr(a) for a in node[2]]
            tmp = self.new_temp()
            self.emit(('CALL', tmp, fname, args))
            return
        if tag == 'RETURN':
            if node[1] is None:
                self.emit(('RET', 0))
            else:
                val = self.emit_expr(node[1])
                self.emit(('RET', val))
            return
        if tag == 'IF':
            cond = self.emit_expr(node[1])
            L_else = self.new_label('L_else_')
            L_end  = self.new_label('L_end_')
            self.emit(('CJZ', cond, L_else))
            self.emit_stmt(node[2])
            self.emit(('JMP', L_end))
            self.emit(('LABEL', L_else))
            if node[3] is not None:
                self.emit_stmt(node[3])
            self.emit(('LABEL', L_end))
            return
        if tag == 'WHILE':
            L_cond = self.new_label('L_cond_')
            L_end  = self.new_label('L_end_')
            self.emit(('LABEL', L_cond))
            cond = self.emit_expr(node[1])
            self.emit(('CJZ', cond, L_end))
            self.emit_stmt(node[2])
            self.emit(('JMP', L_cond))
            self.emit(('LABEL', L_end))
            return
        if tag == 'BLOCK':
            self.emit_block(node)
            return
        if tag == 'FUNCDEF':
            name = node[1]
            params = node[2]
            body = node[3]
            self.emit(('FUNC', name, params))
            self.emit(('LABEL', f'FUNC_{name}'))
            # move implicit arg registers to params
            for i, p in enumerate(params):
                self.emit(('MOV', p, f'_arg{i}'))
            self.emit_block(body)
            # ensure function ends
            self.emit(('RET', 0))
            return
        if tag == 'PROGRAM':
            for s in node[1]:
                self.emit_stmt(s)
            return
        raise ValueError(f"Unsupported stmt: {node}")


def generate_ir(ast) -> List[Instr]:
    b = IRBuilder()
    b.emit_stmt(ast)
    return b.code