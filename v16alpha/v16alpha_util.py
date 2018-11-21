"""
utility functions
"""

from processor import *
from v16alpha.v16alpha import V16alpha
from v16alpha.v16alpha_asm import *


nbEqSigns = 20

def loadProgram(processor, asm, verbose=False):
	p = processor
	prog = assemble(asm)
	if verbose:
		printByteArray(prog, groupBytesBy=3, name="Assembled program")
		print("-"*nbEqSigns+"       Loading program      "+"-"*nbEqSigns)
		
	opIndex=0
	opOperand=0
	progCtrlPinset = p.pinset.pins[6][0]
	ioaPinset = p.pinset.pins[31][0]
	for i in prog:
		if verbose:
			b="{:0>16}".format(bin(opIndex*256 + i)[2:])
			print("{:0>2}".format(hex(i)[2:].upper()), "{:>3}".format(opIndex), opOperand, b[:8], b[8:])
		ioaPinset.state = opIndex*256 + i
		progCtrlPinset.state = opOperand
		
		p.pinset.setPinState(5, True)
		for j in range (4):
			p.pinset.setPinState(0,True)
		
		opOperand+=1
		opOperand%=3
		if opOperand == 0:
			opIndex+=1
			if verbose:
				print()
	if verbose:	
		printByteArray(p.program, groupBytesBy=3, name="Program data")
		print("Cycles :",p.cycleCount)

def run (processor, verbose=False, safety=None):
	p = processor
	
	if verbose:	
		print("-"*nbEqSigns+"     Starting execution     "+"-"*nbEqSigns)
	
	while (p.err.value < 9):
		#p.cycle()
		p.pinset.setPinState(0,True)
		if verbose:
			print(p.err, p.programCounter)
			
		if (safety is not None):
			safety-=1
			if (safety==0):
				print("Interrupted due to safety")
				break
		
		
	if verbose:
		print("Cycles :",p.cycleCount)
		print("-"*nbEqSigns+"       Ended execution      "+"-"*nbEqSigns)
	
	
def reset(p, verbose=False):
	if verbose:
		print("-"*nbEqSigns+"          Resetting         "+"-"*nbEqSigns)
	
	for j in range(5):
		p.pinset.setPinState(5,True)
		p.pinset.setPinState(6,True)
		p.pinset.setPinState(7,True)
		p.pinset.setPinState(0,True)

		
		
def printHeader(symbol,title):
	print(symbol*nbEqSigns+"{:^28}".format(title)+symbol*nbEqSigns)
		
		
		
		