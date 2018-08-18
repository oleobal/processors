#!/usr/bin/python3

from processor import printByteArray

from v16alpha.v16alpha import V16alpha

from v16alpha.v16alpha_asm import *

if __name__ == '__main__' :
	p = V16alpha()
	print(p.err)
	print(p.register)
	print("======     Starting execution     ======")
	prog = assemble("""\
STORE 21 RINT
# cannot write 0xCF, have to compute it
PUSH 157
POP RINO
ADD 50 RINO
DSPR RINO RINT""")
	p.loadProgram(prog)
	#p.loadProgram(bytes([0xA0, 0x0A, 0xD0, 0xFF,0xFF,0xFF,0xCF,0xFF,0xFF]))
	while (p.err.value < 9):
		p.cycle()
		print(p.err, p.programCounter)
	print("======       Ended execution      ======")
	printByteArray(p.program, groupBytesBy=3, name="Program data")
	print(p.register)
	print(p.io)
	print("Cycles :",p.cycleCount)
