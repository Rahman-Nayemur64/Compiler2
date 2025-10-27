import argparse
from lexer import lex
from parsers import Parser
from semantic import Sema, SemaError
from codegen_tac import Codegen
from optimizer import optimize
from asmgen import asm_from_tac

PHASES=["lex","parse","sema","tac","opt","asm","all"]

# -------- pretty printers --------

def banner(title):
    print("*"*60) ; print(f"*** {title}") ; print("*"*60)

def dump_tokens(tokens):
    for t in tokens:
        print(repr(t))

# minimal AST dump (type + key fields)
from ast_nodes import Program, Func, Block, VarDecl, Assign, If, While, Return, Print, Call, Int, Var, BinOp, Unary

def ast_dump(node, indent=0):
    pad = "  "*indent
    def line(h):
        print(pad + h)
    if isinstance(node, Program):
        line("Program:")
        for f in node.funcs: ast_dump(f, indent+1)
    elif isinstance(node, Func):
        line(f"Func {node.name}({', '.join(p.name for p in node.params)}):")
        ast_dump(node.body, indent+1)
    elif isinstance(node, Block):
        line("Block")
        for s in node.stmts: ast_dump(s, indent+1)
    elif isinstance(node, VarDecl):
        line(f"VarDecl {node.name}")
        if node.init: ast_dump(node.init, indent+1)
    elif isinstance(node, Assign):
        line(f"Assign {node.name}") ; ast_dump(node.expr, indent+1)
    elif isinstance(node, If):
        line("If") ; ast_dump(node.cond, indent+1)
        line("Then:") ; ast_dump(node.then, indent+1)
        if node.els:
            line("Else:") ; ast_dump(node.els, indent+1)
    elif isinstance(node, While):
        line("While") ; ast_dump(node.cond, indent+1) ; ast_dump(node.body, indent+1)
    elif isinstance(node, Return):
        line("Return") ; ast_dump(node.expr, indent+1)
    elif isinstance(node, Print):
        line("Print") ; ast_dump(node.expr, indent+1)
    elif isinstance(node, Call):
        line(f"Call {node.name}")
        for a in node.args: ast_dump(a, indent+1)
    elif isinstance(node, Int):
        line(f"Int {node.value}")
    elif isinstance(node, Var):
        line(f"Var {node.name}")
    elif isinstance(node, Unary):
        line(f"Unary {node.op}") ; ast_dump(node.expr, indent+1)
    elif isinstance(node, BinOp):
        line(f"BinOp {node.op}") ; ast_dump(node.left, indent+1) ; ast_dump(node.right, indent+1)
    else:
        line(str(node))

# ---------------------------------

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('file')
    ap.add_argument('--phase', choices=PHASES, default='all')
    args=ap.parse_args()

    src=open(args.file,'r').read()

    # Phase 1: Lex
    toks=lex(src)
    if args.phase in ('lex','all'):
        banner('PHASE 1: LEXICAL TOKENS')
        dump_tokens(toks)
        if args.phase=='lex': return

    # Phase 2: Parse → AST
    ast=Parser(toks).parse()
    if args.phase in ('parse','all'):
        banner('PHASE 2: PARSE (AST)')
        ast_dump(ast)
        if args.phase=='parse': return

    # Phase 3: Semantic
    if args.phase in ('sema','all'):
        banner('PHASE 3: SEMANTIC ANALYSIS')
        try:
            Sema(ast).run()
            print('OK: no semantic errors.')
        except SemaError as e:
            print('SemanticError:', e) ; return
        if args.phase=='sema': return
    else:
        # still run to validate downstream phases
        Sema(ast).run()

    # Phase 4: TAC
    tac=Codegen(ast).run()
    if args.phase in ('tac','all'):
        banner('PHASE 4: THREE-ADDRESS CODE (TAC)')
        print("\n".join(tac))
        if args.phase=='tac': return

    # Phase 5: Optimizer
    tac_opt=optimize(tac)
    if args.phase in ('opt','all'):
        banner('PHASE 5: OPTIMIZED TAC')
        print("\n".join(tac_opt))
        if args.phase=='opt': return

    # Phase 6: ASM gen
    asm=asm_from_tac(tac_opt)
    if args.phase in ('asm','all'):
        banner('PHASE 6: ASM (Toy Stack VM)')
        print("\n".join(asm))

if __name__=='__main__':
    main()




