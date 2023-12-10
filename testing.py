instruction= "Load R1, 0(R2)"
Busy = True
Op = instruction.split()[0]
operands = instruction.split()[1:]
ra=operands[0].split(",")[0]
offset = operands[1].split("(")[0]
rB = operands[1].split("(")[1].replace(")", "")
A = offset
Vj = rB
print("A",A)
print("Vj",Vj)
print("Op",Op)
print("ra",ra)