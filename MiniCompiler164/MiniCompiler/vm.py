import re

def parse_token(tok, registers, memory):
    tok = str(tok).strip().rstrip(',')
    try:
        return int(tok)
    except ValueError:
        pass
    if tok in memory:
        return memory[tok]
    return registers.get(tok, 0)

def run_machine_code(lines, *, max_steps=500_000, trace=False):
    if isinstance(lines, str):
        lines = [l.strip() for l in lines.splitlines() if l.strip()]

    # Build label map
    label_map = {}
    for i, line in enumerate(lines):
        if line.startswith('LABEL'):
            parts = line.split()
            if len(parts) >= 2:
                label_map[parts[1]] = i

    registers = {}
    memory = {}
    ip = 0
    output = []
    steps = 0
    callstack = []  # stores return ip

    def step_debug():
        if not trace:
            return
        print(f"[ip={ip:04d}] {lines[ip]}  | regs={registers}")

    while ip < len(lines):
        if steps >= max_steps:
            raise RuntimeError(f"Execution step limit exceeded ({max_steps}).")
        steps += 1

        line = lines[ip].strip()
        if not line or line.startswith('//'):
            ip += 1; continue
        if line.startswith('LABEL'):
            ip += 1; continue

        parts = line.split()
        op = parts[0]
        step_debug()

        if op == 'MOV':
            dest = parts[1].rstrip(',')
            val = parse_token(parts[2], registers, memory)
            registers[dest] = val
            ip += 1; continue

        if op in ('+','-','*','/'):
            dest = parts[1].rstrip(',')
            a = parse_token(parts[2], registers, memory)
            b = parse_token(parts[3], registers, memory)
            if op == '+': registers[dest] = a + b
            elif op == '-': registers[dest] = a - b
            elif op == '*': registers[dest] = a * b
            elif op == '/': registers[dest] = a // b if b != 0 else 0
            ip += 1; continue

        if op in ('GT','LT','EQ','NE','GE','LE'):
            dest = parts[1].rstrip(',')
            a = parse_token(parts[2], registers, memory)
            b = parse_token(parts[3], registers, memory)
            registers[dest] = int(
                (op == 'GT' and a > b) or
                (op == 'LT' and a < b) or
                (op == 'EQ' and a == b) or
                (op == 'NE' and a != b) or
                (op == 'GE' and a >= b) or
                (op == 'LE' and a <= b)
            )
            ip += 1; continue

        if op == 'JMP':
            label = parts[1]
            if label not in label_map:
                raise RuntimeError(f'Unknown label: {label}')
            ip = label_map[label]
            continue

        if op == 'JZ':
            reg = parts[1].rstrip(',')
            label = parts[2]
            val = parse_token(reg, registers, memory)
            if val == 0:
                if label not in label_map:
                    raise RuntimeError(f'Unknown label: {label}')
                ip = label_map[label]
                continue
            ip += 1; continue

        if op == 'CALL':
            # CALL name, nargs
            name = parts[1].rstrip(',')
            # push return address
            callstack.append(ip + 1)
            label = f'FUNC_{name}'
            if label not in label_map:
                raise RuntimeError(f'Unknown function: {name}')
            ip = label_map[label]
            continue

        if op == 'RET':
            val = parse_token(parts[1], registers, memory) if len(parts) > 1 else 0
            registers['_ret'] = val
            if not callstack:
                # return at top level: just stop
                break
            ip = callstack.pop()
            continue

        if op == 'PRINT':
            val = parse_token(parts[1], registers, memory)
            output.append(str(val))
            print(val)
            ip += 1; continue

        m = re.match(r'^(?P<lhs>\w+)\s*=\s*(?P<rhs>.+)$', line)
        if m:
            lhs = m.group('lhs')
            rhs = m.group('rhs')
            for k, v in registers.items():
                rhs = re.sub(r'\b' + re.escape(k) + r'\b', str(v), rhs)
            try:
                val = int(eval(rhs))
            except Exception:
                val = 0
            registers[lhs] = val
            ip += 1; continue

        raise ValueError(f"Unknown instruction: '{line}'")

    return {'registers': registers, 'memory': memory, 'output': output}