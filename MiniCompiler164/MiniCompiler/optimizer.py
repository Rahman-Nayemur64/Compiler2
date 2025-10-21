from typing import List, Tuple, Union

TInstr = Tuple
TOperand = Union[int, str]

ARITH = {'+', '-', '*', '/'}
RELOP = {'<','<=','>','>=','==','!='}

def is_int(x):
    return isinstance(x, int)

def optimize_ir(ir_code: List[TInstr]) -> List[TInstr]:
    out: List[TInstr] = []
    for instr in ir_code:
        if not instr:
            continue
        op = instr[0]
        if op == 'BIN':
            _, dst, bop, a, b = instr
            if is_int(a) and is_int(b):
                if bop in ARITH or bop in RELOP:
                    if bop == '+':  val = a + b
                    elif bop == '-': val = a - b
                    elif bop == '*': val = a * b
                    elif bop == '/': val = a // b if b != 0 else 0
                    elif bop == '<':  val = int(a <  b)
                    elif bop == '<=': val = int(a <= b)
                    elif bop == '>':  val = int(a >  b)
                    elif bop == '>=': val = int(a >= b)
                    elif bop == '==': val = int(a == b)
                    elif bop == '!=': val = int(a != b)
                    out.append(('MOV', dst, val))
                    continue
        out.append(instr)

    # Remove MOV x,x
    tmp = []
    for instr in out:
        if instr[0] == 'MOV' and isinstance(instr[2], str) and instr[1] == instr[2]:
            continue
        tmp.append(instr)
    out = tmp

    return out