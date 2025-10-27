import re

def optimize(tac_lines):
    # very small: remove "x = x" and fold simple const ops
    out=[]
    constbin=re.compile(r"^(t\d+) = (\d+) ([+\-*/%]|==|!=|<=|<|>=|>) (\d+)$")
    for ln in tac_lines:
        if re.match(r"^(\w+) = \1$", ln):
            continue
        m=constbin.match(ln)
        if m:
            t,a,op,b=m.groups(); a=int(a); b=int(b)
            val=None
            if op=='+': val=a+b
            elif op=='-': val=a-b
            elif op=='*': val=a*b
            elif op=='/': val=a//b if b!=0 else a
            elif op=='%': val=a%b if b!=0 else 0
            elif op=='<': val=int(a<b)
            elif op=='<=': val=int(a<=b)
            elif op=='>': val=int(a>b)
            elif op=='>=': val=int(a>=b)
            elif op=='==': val=int(a==b)
            elif op=='!=': val=int(a!=b)
            out.append(f"{t} = {val}"); continue
        out.append(ln)
    return out









