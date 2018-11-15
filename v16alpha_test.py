#!/usr/bin/python3

from processor import *

from v16alpha.v16alpha import V16alpha

from v16alpha.v16alpha_asm import *


def testV16alpha():
	
	nbEqSigns = 20
	
	p = V16alpha()
	print(p.err)
	print(p.register)
	prog = assemble("""\
STORE 21 RINT
# cannot write 0xCF, have to compute it
PUSH 157
POP RINO
ADD 50 RINO
DSPR RINO RINT""")
	#p.loadProgram(prog)
	#p.loadProgram(bytes([0xA0, 0x0A, 0xD0, 0xFF,0xFF,0xFF,0xCF,0xFF,0xFF]))
	printByteArray(prog, groupBytesBy=3, name="Assembled program")
	print("="*nbEqSigns+"       Loading program      "+"="*nbEqSigns)
	opIndex=0
	opOperand=0
	progCtrlPinset = p.pinset.pins[6][0]
	ioaPinset = p.pinset.pins[31][0]
	for i in prog:
		b="{:0>16}".format(bin(opIndex*256 + i)[2:])
		print(hex(i)[2:].upper(), opIndex, opOperand, b[:8], b[8:])
		ioaPinset.state = opIndex*256 + i
		progCtrlPinset.state = opOperand
		
		p.pinset.setPinState(5, True)
		for j in range (4):
			p.pinset.setPinState(0,True)
		
		opOperand+=1
		opOperand%=3
		if opOperand == 0:
			opIndex+=1
			print()
	
	printByteArray(p.program, groupBytesBy=3, name="Program data")
	print("Cycles :",p.cycleCount)
	print("="*nbEqSigns+"     Starting execution     "+"="*nbEqSigns)
	
	while (p.err.value < 9):
		#p.cycle()
		p.pinset.setPinState(0,True)
		print(p.err, p.programCounter)
	print("="*nbEqSigns+"       Ended execution      "+"="*nbEqSigns)
	printByteArray(p.program, groupBytesBy=3, name="Program data")
	print(p.register)
	print(p.io)
	print(p.pinset)
	print("Cycles :",p.cycleCount)
	print("="*nbEqSigns+"          Resetting         "+"="*nbEqSigns)
	for j in range(5):
		p.pinset.setPinState(5,True)
		p.pinset.setPinState(6,True)
		p.pinset.setPinState(7,True)
		p.pinset.setPinState(0,True)
	printByteArray(p.program, groupBytesBy=3, name="Program data")
	print(p.register)
	print(p.pinset)
	print("Cycles :",p.cycleCount)
	
	



if __name__ == '__main__' :
	testV16alpha()