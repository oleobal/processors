#!/usr/bin/python3

from processor import *

from v16alpha import V16alpha

from v16alpha_asm import *

if __name__ == '__main__' :
	p = V16alpha()
	print(p.err)
	print(p.register)
	print("======     Starting execution     ======")
	prog = compileASM("""\
STORE 10 RINT
STORE 0x55 RINO
END""")
	p.loadProgram(prog)
	#p.loadProgram(bytes([0xA0, 0x0A, 0xD0, 0xFF,0xFF,0xFF,0xCF,0xFF,0xFF]))
	while (p.err.value < 9):
		p.cycle()
		print(p.err)
		print(p.programCounter)
	print("======       Ended execution      ======")
	printByteArray(p.program, groupBytesBy=3, name="Program data")
	print(p.register)
	print(p.io)
	print("Cycles :",p.cycleCount)
