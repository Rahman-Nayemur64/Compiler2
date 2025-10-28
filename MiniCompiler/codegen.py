from typing import List, Tuple, Union

Instr = Tuple
Operand = Union[int, str]

RELOP_MAP = {
    '>': 'GT', '<': 'LT', '==': 'EQ', '!=': 'NE', '>=': 'GE', '<=': 'LE'
}

def tok(x: Operand) -> str:
    return str(x)

def generate_machine_code(ir_code: List[Instr]) -> List[str]:
    mc: List[str] = []
    functions = set()

    for instr in ir_code:
        if not instr:
            continue
        op = instr[0]
        if op == 'FUNC':
            _, name, _params = instr
            functions.add(name)
            continue  # marker only
        if op == 'LABEL':
            _, name = instr
            mc.append(f"LABEL {name}")
            continue
        if op == 'JMP':
            mc.append(f"JMP {instr[1]}")
            continue
        if op == 'CJZ':
            _, cond, label = instr
            mc.append(f"JZ {tok(cond)}, {label}")
            continue
        if op == 'MOV':
            _, dst, src = instr
            mc.append(f"MOV {tok(dst)}, {tok(src)}")
            continue
        if op == 'BIN':
            _, dst, bop, a, b = instr
            if bop in ('+','-','*','/'):
                mc.append(f"{bop} {tok(dst)}, {tok(a)}, {tok(b)}")
            else:
                mc.append(f"{RELOP_MAP[bop]} {tok(dst)}, {tok(a)}, {tok(b)}")
            continue
        if op == 'CALL':
            _, dst, name, args = instr
            # move args to _arg{i}
            for i, a in enumerate(args):
                mc.append(f"MOV _arg{i}, {tok(a)}")
            mc.append(f"CALL {name}, {len(args)}")
            if dst is not None:
                mc.append(f"MOV {tok(dst)}, _ret")
            continue
        if op == 'RET':
            _, val = instr
            mc.append(f"RET {tok(val)}")
            continue
        mc.append("// UNKNOWN: " + repr(instr))

    # Bootstrap: if 'main' defined, call it automatically at end
    if 'main' in functions:
        mc.append("CALL main, 0")
    return mc