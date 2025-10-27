# Converts TAC to simple stack-VM assembly.
# Supported ops: PUSH n, LOAD x, STORE x, ADD,SUB,MUL,DIV,MOD, CMP<,CMP<=,CMP>,CMP>=,CMPEQ,CMPNE, JZ label, JMP label, LABEL, CALL name n, RET, PARAM

import re

def asm_from_tac(tac):
    asm=[]
    def label(name): asm.append(f"LABEL {name}")
    for ln in tac:
        if ln.startswith('func '):
            asm.append(f"; {ln}")
            continue
        if ln.startswith('endfunc'):
            asm.append('; endfunc')
            continue
        if m:=re.match(r"(\w+) = (\d+)$", ln):
            var,val=m.groups(); asm+= [f"PUSH {val}", f"STORE {var}"]; continue
        if m:=re.match(r"(\w+) = (\w+)$", ln):
            var,src=m.groups(); asm+= [f"LOAD {src}", f"STORE {var}"]; continue
        if m:=re.match(r"(\w+) = (\w+) ([+\-*/%]|==|!=|<=|<|>=|>) (\w+)$", ln):
            dst,a,op,b=m.groups();
            asm+= [f"LOAD {a}", f"LOAD {b}"]
            opmap={'+':'ADD','-':'SUB','*':'MUL','/':'DIV','%':'MOD','<':'CMP<','<=':'CMP<=','>':'CMP>','>=':'CMP>=','==':'CMPEQ','!=':'CMPNE'}
            asm.append(opmap[op])
            asm.append(f"STORE {dst}")
            continue
        if m:=re.match(r"param (\w+)$", ln): asm.append(f"PARAM {m.group(1)}"); continue
        if m:=re.match(r"call (\w+), (\d+)$", ln): asm.append(f"CALL {m.group(1)} {m.group(2)}"); continue
        if m:=re.match(r"(t\d+) = call (\w+), (\d+)$", ln):
            t,fn,argc=m.groups(); asm.append(f"CALL {fn} {argc}"); asm.append(f"STORE {t}"); continue
        if m:=re.match(r"return (\w+)$", ln): asm+= [f"LOAD {m.group(1)}","RET"]; continue
        if m:=re.match(r"(L_[\w]+_\d+):$", ln): label(m.group(1)); continue
        if m:=re.match(r"if (\w+) goto (\w+)$", ln):
            tmp=m.group(1); lab=m.group(2)
            asm+= [f"LOAD {tmp}", f"JZ skip_{lab}", f"JMP {lab}", f"LABEL skip_{lab}"]
            continue
        if m:=re.match(r"goto (\w+)$", ln): asm.append(f"JMP {m.group(1)}"); continue
        # raw labels like L_then_1:
        if ln.endswith(':'): label(ln[:-1]); continue
        # comments or unknown
        asm.append(f"; {ln}")
    return asm





