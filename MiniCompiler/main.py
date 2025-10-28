# Mini Compiler Main Script (clean, sectioned output)
import sys, os, shutil
from typing import Any, List, Tuple

from lexer import tokenize
from my_parser import Parser
from semantic import build_symbol_table
from ir import generate_ir
from optimizer import optimize_ir
from codegen import generate_machine_code
from vm import run_machine_code

# ========== Pretty Printing Helpers ==========
ANSI = {
    "reset": "\x1b[0m",
    "bold": "\x1b[1m",
    "cyan": "\x1b[36m",
    "magenta": "\x1b[35m",
    "yellow": "\x1b[33m",
    "green": "\x1b[32m",
    "blue": "\x1b[34m",
}

def supports_color() -> bool:
    return sys.stdout.isatty() and os.environ.get("NO_COLOR") is None

USE_COLOR = supports_color()

def c(text: str, color: str) -> str:
    if not USE_COLOR:
        return text
    return f"{ANSI.get(color, '')}{text}{ANSI['reset']}"

def rule(width: int = None) -> str:
    if width is None:
        width = shutil.get_terminal_size((100, 20)).columns
    return "\n" + ("-" * max(40, min(width, 120))) + "\n"

def header(title: str) -> None:
    bar = "=" * len(title)
    print(rule())
    print(c(title, "magenta"))
    print(c(bar, "magenta"))

# ----- Token formatting -----
Token = Tuple[str, Any]

def format_tokens(tokens):
    def display_kind(kind, lexeme):
        if kind == 'ID':
            low = lexeme.lower()
            if low == 'int':   return 'INT'
            if low == 'bool':  return 'BOOL'
            if low == 'if':    return 'IF'
            if low == 'else':  return 'ELSE'
            if low == 'while': return 'WHILE'
            if low == 'func':  return 'FUNC'
            if low == 'return':return 'RETURN'
        if kind == 'END':    return 'SEMI'
        if kind == 'NUMBER': return 'INT_LIT'
        if kind == 'LBRACE': return 'LBRACE'
        if kind == 'RBRACE': return 'RBRACE'
        if kind == 'COMMA':  return 'COMMA'
        return kind
    rows = []
    for t in tokens:
        if len(t) >= 4:
            kind, lexeme, ln, col = t[0], t[1], t[2], t[3]
        else:
            kind, lexeme = t[0], t[1]
            ln, col = 0, 0
        dkind = display_kind(kind, lexeme)
        rows.append((dkind, lexeme, ln, col))
    kind_w = max((len(k) for k, _, _, _ in rows), default=4)
    lex_w  = max((len(repr(s)) for _, s, _, _ in rows), default=3)
    lines = [f"{k.ljust(kind_w)}  {repr(s).ljust(lex_w)}  ({ln}:{col})" for k, s, ln, col in rows]
    return "\n".join(lines)


# ----- AST pretty printer -----

def format_ast(node: Any, indent: int = 0) -> str:
    sp = " " * indent
    if not isinstance(node, tuple):
        return sp + repr(node)
    tag = node[0]
    if tag == 'PROGRAM':
        children = "\n".join(format_ast(ch, indent + 2) for ch in node[1])
        return f"{sp}PROGRAM\n{children}"
    if tag == 'ASSIGN':
        lhs = node[1]
        rhs = format_ast(node[2], 0).strip()
        return f"{sp}ASSIGN {lhs} = {rhs}"
    if tag == 'NUM':
        return f"{sp}NUM({node[1]})"
    if tag == 'VAR':
        return f"{sp}VAR({node[1]})"
    if tag == 'BIN_OP':
        op = node[1]
        left = format_ast(node[2], 0).strip()
        right = format_ast(node[3], 0).strip()
        return f"{sp}({left} {op} {right})"
    if tag == 'IF':
        cond = format_ast(node[1], 0).strip()
        then_s = format_ast(node[2], indent + 2)
        else_part = node[3]
        out = f"{sp}IF {cond}\n{sp}  THEN:\n{then_s}"
        if else_part is not None:
            out += f"\n{sp}  ELSE:\n" + format_ast(else_part, indent + 2)
        return out
    if tag == 'WHILE':
        cond = format_ast(node[1], 0).strip()
        body = format_ast(node[2], indent + 2)
        return f"{sp}WHILE {cond}\n{body}"
    return sp + repr(node)

# ----- IR formatting -----

def format_ir(ir_code):
    out = []
    for instr in ir_code:
        if not instr:
            continue
        op = instr[0]
        if op == 'FUNC':
            _, name, params = instr
            out.append(f"FUNC {name}({', '.join(params)})")
        elif op == 'LABEL':
            out.append(f"LABEL {instr[1]}")
        elif op == 'JMP':
            out.append(f"JMP {instr[1]}")
        elif op == 'CJZ':
            out.append(f"CJZ {instr[1]}, {instr[2]}")
        elif op == 'MOV':
            _, d, s = instr
            out.append(f"{d} = {s}")
        elif op == 'BIN':
            _, d, bop, a, b = instr
            out.append(f"{d} = {a} {bop} {b}")
        elif op == 'CALL':
            _, d, name, args = instr
            out.append(f"{d} = CALL {name}({', '.join(map(str, args))})")
        elif op == 'RET':
            _, v = instr
            out.append(f"RET {v}")
        else:
            out.append(str(instr))
    return "\n".join(out)

# ----- Machine code formatting -----

def format_machine_code(code: List[str]) -> str:
    out = []
    for line in code:
        if line.startswith('LABEL'):
            out.append("")
            out.append(c(line, 'yellow'))
        elif line.startswith(('JZ', 'JMP')):
            out.append(c(line, 'cyan'))
        elif line.startswith(('GT','LT','EQ','NE','GE','LE')):
            out.append(c(line, 'blue'))
        else:
            out.append(line)
    return "\n".join(out)

# ========== Core runner ==========

def read_source_from_file(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as fh:
        return fh.read()


def run_source(code: str) -> None:
    header("Source Code")
    print(c("""""" + code.strip() + """""", 'green'))

    # LEXER
    tokens_full = tokenize(code)  # [(KIND, LEXEME, LINE, COL)]
    header("Tokens")
    print(format_tokens(tokens_full))

    # For the parser, convert to (KIND, VALUE) as it expects
    tokens = []
    for kind, lexeme, ln, col in tokens_full:
        if kind == "NUMBER":
            # parser expects int for numeric tokens
            tokens.append((kind, int(lexeme)))
        else:
            tokens.append((kind, lexeme))

    # PARSER
    parser = Parser(tokens)
    ast = parser.parse()
    header("AST")
    print(format_ast(ast))

    # SEMANTIC (symbol table)
    symbols = build_symbol_table(ast)
    header("Semantic (Symbol Table)")
    if symbols:
        width = max(len(k) for k in symbols)
        for k, v in symbols.items():
            print(f"{k.ljust(width)} : {v}")
    else:
        print("<empty>")

    # IR
    ir_code = generate_ir(ast)
    header("IR (Three-Address Code)")
    print(format_ir(ir_code))

    # Optimizer
    optimized_ir = optimize_ir(ir_code)
    header("Optimized IR")
    print(format_ir(optimized_ir))

    # Codegen
    machine_code = generate_machine_code(optimized_ir)
    header("Machine Code")
    print(format_machine_code(machine_code))

    # VM
    header("Execution")
    res = run_machine_code(machine_code if isinstance(machine_code, list) else list(machine_code))
    print("Registers:", res.get('registers'))
    print("Output:", res.get('output'))


if __name__ == "__main__":
    fname = None
    # prefer first command-line arg
    if len(sys.argv) > 1:
        fname = sys.argv[1]
    # else look for program.src in current folder
    elif os.path.exists("program.src"):
        fname = "program.src"
    # else look in the package folder
    elif os.path.exists(os.path.join(os.path.dirname(__file__), "program.src")):
        fname = os.path.join(os.path.dirname(__file__), "program.src")

    if fname and os.path.exists(fname):
        code = read_source_from_file(fname)
    else:
        # fallback sample program
        code = (
            """
            x = 1; y = 0;
            while (x <= 5) x = x + 1;
            if (x > 5) y = 100;
            """.strip()
        )

    try:
        run_source(code)
    except Exception as e:
        header("Error")
        print(c(type(e).__name__ + ": " + str(e), 'red'))
