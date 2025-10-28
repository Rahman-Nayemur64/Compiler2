# Semantic Analysis Phase
def build_symbol_table(ast):
    symbols = {}
    def visit(node):
        if node[0] == 'ASSIGN':
            var_name = node[1]
            expr = node[2]
            symbols[var_name] = evaluate_expr(expr, symbols)
        elif node[0] == 'PROGRAM':
            for stmt in node[1]:
                visit(stmt)
    visit(ast)
    return symbols

def evaluate_expr(expr, symbols):
    if expr[0] == 'NUM':
        return expr[1]
    elif expr[0] == 'VAR':
        return symbols.get(expr[1], 0)
    elif expr[0] == 'BIN_OP':
        left = evaluate_expr(expr[2], symbols)
        right = evaluate_expr(expr[3], symbols)
        if expr[1] == '+': return left + right
        if expr[1] == '-': return left - right
        if expr[1] == '*': return left * right
        if expr[1] == '/': return left / right
    return 0
