#!/usr/bin/python3

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

		
		
		
		
		
		
		
		
		
		
		
		
		
def testBasicAndReset(p, verbose=False):
	if (verbose):
		print("="*nbEqSigns+"       BasicAndReset        "+"="*nbEqSigns)
	if verbose:
		print(p.err)
		print(p.register)
	asm="""\
STORE 21 RINT
# cannot write 0xCF, have to compute it
PUSH 157
POP RINO
ADD 50 RINO
DSPR RINO RINT"""
	loadProgram(p, asm, verbose)
	run(p, verbose)
	
	if verbose:
		printByteArray(p.program, groupBytesBy=3, name="Program data")
		print(p.register)
		print(p.io)
		print(p.pinset)
	
	assert p.program[21] == 0xCF
	assert p.err.value == 9
	
	reset(p,verbose)
	
	assert p.program == bytearray([0xFF]*2**V16alpha.INSTRUCTION_ADDRESSING_SIZE*V16alpha.INSTRUCTION_SIZE)
	assert p.pinset.state == [False]*32
	assert p.err.value == 0
	
	
	if verbose:
		printByteArray(p.program, groupBytesBy=3, name="Program data")
		print(p.register)
		print(p.pinset)
		print("Cycles :",p.cycleCount)

	
	
	
	
def testConstantAndStaticLabels(p, verbose=False):
	if (verbose):
		print("="*nbEqSigns+"  ConstantAndStaticLabels   "+"="*nbEqSigns)

	# by hand
	asm1 ="""\
STORE 5 RINT
STORE RINT RCNT

PUSH 1 # these stack ops will be skipped
POP RINO
PUSH 1
POP RINO

END"""
	# with constants
	asm2 ="""\
:CONST lol 5
STORE :lol RINT
STORE RINT RCNT
PUSH 1
POP  RINO
PUSH 1
 POP RINO
END"""
	# with static label
	asm3 ="""\
STORE :endline RINT
STORE  RINT    RCNT
PUSH 1
POP RINO
PUSH 1
:endline: POP RINO
END"""
	prog1 = assemble(asm1)
	prog2 = assemble(asm2)
	prog3 = assemble(asm3)
	assert prog1 == prog2 and prog2 == prog3
	
	loadProgram(p, asm3, verbose)
	run(p, verbose)
	
	
def testDynamicJump(p, verbose=False):
	if (verbose):
		print("="*nbEqSigns+"        DynamicJump        "+"="*nbEqSigns)
	
	asm="""
		STORE 1 RIOB
		LABEL 0
		store 2 RIOB
		JUMP 14
		LABEL 121
		store 3 RIOB
		END
		LABEL 14
		store 4 RIOB
		END
		LABEL 23
		store 5 RIOB
		END
		"""
	loadProgram(p, asm, verbose)
	run(p, verbose, safety=100)
	
	if verbose:
		print(p.pinset)
	
	# RIOB = 4
	assert(p.pinset.getPinState(8)  == False)
	assert(p.pinset.getPinState(9)  == False)
	assert(p.pinset.getPinState(10) == False)
	assert(p.pinset.getPinState(11) == False)
	assert(p.pinset.getPinState(12) == False)
	assert(p.pinset.getPinState(13) == True)
	assert(p.pinset.getPinState(14) == False)
	assert(p.pinset.getPinState(15) == False)
		
if __name__ == '__main__' :
	verbose = False
	from sys import argv
	if "-v" in argv:
		verbose = True
	
	p = V16alpha()
	
	testBasicAndReset(p, verbose)
	reset(p)
	
	testConstantAndStaticLabels(p, verbose)
	reset(p)
	
	testDynamicJump(p, True)
	reset(p)