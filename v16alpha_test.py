#!/usr/bin/python3

from processor import *

from v16alpha.v16alpha import V16alpha
from v16alpha.v16alpha_asm import *
from v16alpha.v16alpha_util import *
		
		
def testBasicAndReset(p, verbose=False):
	if (verbose):
		print("="*nbEqSigns+"       BasicAndReset        "+"="*nbEqSigns)
	if verbose:
		print(p.err)
		print(p.register)
	asm="""\
STORE 21 RINO
# cannot write 0xCF, have to compute it
PUSH 157
POP RINT
ADD 50
DSPR RINT RINO"""
	loadProgram(p, asm, verbose)
	run(p, verbose)
	
	if verbose:
		printByteArray(p.program, groupBytesBy=3, name="Program data")
		print(p.register)
		print(p.io)
		print("{:indic}".format(p.pinset))
	
	assert p.program[21] == 0xCF
	assert p.err.value == 9
	
	reset(p,verbose)
	
	assert p.program == bytearray([0xFF]*2**V16alpha.INSTRUCTION_ADDRESSING_SIZE*V16alpha.INSTRUCTION_SIZE)
	assert p.pinset.state == [False]*32
	assert p.err.value == 0
	
	
	if verbose:
		printByteArray(p.program, groupBytesBy=3, name="Program data")
		print(p.register)
		print("{:indic}".format(p.pinset))
		print("Cycles :",p.cycleCount)

	
	
	
	
def testConstantAndStaticLabels(p, verbose=False):
	if (verbose):
		print("="*nbEqSigns+"  ConstantAndStaticLabels   "+"="*nbEqSigns)

	# by hand
	asm1 ="""
		STORE 5 RINT
		STORE RINT RCNT

		PUSH 1 # these stack ops will be skipped
		POP RINO
		PUSH 1
		POP RINO

		END
		"""
	# with constants
	asm2 ="""
		:CONST lol 5
		STORE !lol RINT
		STORE RINT RCNT
		PUSH 1
		POP  RINO
		PUSH 1
		 POP RINO
		END
		"""
	# with static label
	asm3 ="""
		STORE !endline RINT
		STORE  RINT    RCNT
		PUSH 1
		POP RINO
		PUSH 1
		:endline: POP RINO
		END
		"""
	prog1 = assemble(asm1)
	prog2 = assemble(asm2)
	prog3 = assemble(asm3)
	assert prog1 == prog2 and prog2 == prog3
	
	loadProgram(p, asm3, verbose)
	run(p, verbose)
	
	
def testDynamicJump(p, verbose=False):
	if (verbose):
		print("="*nbEqSigns+"         DynamicJump        "+"="*nbEqSigns)
	
	asm="""
		STORE 1 RIOB
		LABEL 0
		store 0x08 rioa
		store 2 RIOB
		JUMP 14
		LABEL 121 # will be skipped
		store 0x0f rioa # if RIOA ends with 1111 skipping didn't work
		store 3 RIOB
		END
		0xFF
		0xFF
		0xFF
		LABEL 14 # jump target
		store 4 RIOB
		END
		LABEL 23 # won't get executed
		store 5 RIOB
		END
		"""
	loadProgram(p, asm, verbose)
	run(p, verbose, safety=100)
	
	if verbose:
		print("{:indic}".format(p.pinset))
	
	assert(getIntFromBoolList(p.pinset.state) == 0b01001000000001000000000000001000)



def testArithmetic(p, verbose=False):
	if (verbose):
		print("="*nbEqSigns+"          Arithmetic        "+"="*nbEqSigns)
	
	if verbose:
		print("-"*nbEqSigns+"             AND            "+"-"*nbEqSigns)
	asm="""
		STORE 0b01010101 RINT
		AND   0b00001111
		#       00000101
		STORE RINT RIOB
		END
		"""
	loadProgram(p, asm, verbose)
	run(p, verbose, safety=100)
	if verbose:
		print("{:indic}".format(p.pinset))
	assert(getIntFromBoolList(p.pinset.state) & 0x00FF0000 == 0b00001010000000000000000)
	reset(p, verbose)
	if verbose:
		print("-"*nbEqSigns+"              OR            "+"-"*nbEqSigns)
	asm="""
		STORE 0b01010101 RINT
		OR    0b00001111
		#       01011111
		STORE RINT RIOB
		END
		"""
	loadProgram(p, asm, verbose)
	run(p, verbose, safety=100)
	if verbose:
		print("{:indic}".format(p.pinset))

	assert(getIntFromBoolList(p.pinset.state) & 0x00FF0000 == 0b010111110000000000000000)
	reset(p, verbose)
	
	if verbose:
		print("-"*nbEqSigns+"             XOR            "+"-"*nbEqSigns)
	asm="""
		STORE 0b01010101 RINT
		XOR   0b00001111
		#       01011010
		STORE RINT RIOB
		END
		"""
	loadProgram(p, asm, verbose)
	run(p, verbose, safety=100)
	if verbose:
		print("{:indic}".format(p.pinset))
	assert(getIntFromBoolList(p.pinset.state) & 0x00FF0000 == 0b010110100000000000000000)


def testConditionals(p, verbose=True):
	if (verbose):
		print("="*nbEqSigns+"        Conditionals        "+"="*nbEqSigns)
	
	asm="""
		STORE 0 RIOB
		STORE 50 RINT
		IF RINT = 0       # false
		END
		IF RINT >= 0      # true
		STORE RINT RIOB
		if rint lt riob   # false
		STORE 100 RIOB
		ifle rint riob    # true
		store 0b01010101 riob
		if riob /= 0x55   # false
		store 0 riob
		if riob > 0       # true
		END
		store 0 riob
		end
		"""
	loadProgram(p, asm, verbose)
	run(p, verbose, safety=100)
	if verbose:
		print("{:indic}".format(p.pinset))
	assert(getIntFromBoolList(p.pinset.state) & 0x00FF0000 == 0b010101010000000000000000)



def testLinstructions(p, verbose=False):
	if (verbose):
		print("="*nbEqSigns+"       L-instructions       "+"="*nbEqSigns)
	asm="""
		LSTORE 257
		STORE RINT RIOA
		END
		"""
	loadProgram(p,asm,verbose)
	run(p,verbose)
	
	if verbose:
		print("{:indic}".format(p.pinset))
	assert(getIntFromBoolList(p.pinset.state) & 0x0000FFFF == 0x0101)
	
	reset(p, verbose)
	asm="""
		LSTORE 0x0FFF
		LADD   0xF000
		STORE RINT RIOA
		END
		"""
	loadProgram(p,asm,verbose)
	run(p,verbose)
	
	if verbose:
		print("{:indic}".format(p.pinset))
	assert(getIntFromBoolList(p.pinset.state) & 0x0000FFFF == 0xFFFF)
	
	reset(p, verbose)
	asm="""
		Store 0b01010101 Rint
		LXOR   0xFFFF
		STORE RINT RIOA
		END
		"""
	loadProgram(p,asm,verbose)
	run(p,verbose)
	
	if verbose:
		print("{:indic}".format(p.pinset))
	assert(getIntFromBoolList(p.pinset.state) & 0x0000FFFF == 0xFFAA)


def testBitShift(p, verbose=False):
	if (verbose):
		printHeader("=", "Bit Shifting")
	asm="""
		LSTORE 0xAAAA
		STORE RINT RIOA
		RIOA >> 1
		END
		"""
	loadProgram(p,asm,verbose)
	run(p,verbose)
	if verbose:
		print(p.register)
		print(p.ioa)
		print(p.pinset)
	assert(getIntFromBoolList(p.pinset.state) & 0x0000FFFF == 0x5555)
	reset(p, verbose)
	asm="""
		LSTORE 0x00FF
		STORE RINT RIOA
		LSHIFT RIOA 4
		RIOA LSHIFT 2
		END
		"""
	loadProgram(p,asm,verbose)
	run(p,verbose)
	if verbose:
		print(p.register)
		print(p.ioa)
		print(p.pinset)
	assert(getIntFromBoolList(p.pinset.state) & 0x0000FFFF == 0x3FC0)
	reset(p, verbose)
	asm="""
		STORE 100 RIOB
		LSTORE 0x0FF0
		STORE RINT RIOA
		RIOA RSHIFT RIOB
		END
		"""
	loadProgram(p,asm,verbose)
	run(p,verbose)
	if verbose:
		print("{:indic}".format(p.pinset))
	assert(getIntFromBoolList(p.pinset.state) & 0x0000FFFF == 0x0000)


def testIOAsubRegs(p,verbose):
	if (verbose):
		printHeader("=", "I/O A sub-registers")
	asm="""
		LSTORE 0
		STORE RINT RIOA
		STORE 0x99  RINT
		STORE RINT RIOAL
		END
		"""
	loadProgram(p,asm,verbose)
	run(p,verbose)
	if verbose:
		print(p.ioa)
	assert(getIntFromBoolList(p.pinset.state) & 0x0000FFFF == 0x9900)

	reset(p, verbose)
	asm="""
		LSTORE 0
		STORE RINT RIOA
		STORE 0x55  RINT
		STORE RINT RIOAL
		ADD 0x55
		STORE RINT RIOAR
		END
		"""
	loadProgram(p,asm,verbose)
	run(p,verbose)
	if verbose:
		print(p.ioa)
	assert(getIntFromBoolList(p.pinset.state) & 0x0000FFFF == 0x55AA)

	reset(p, verbose)
	asm="""
		STORE 0x55  RINTL
		ADD 0x55
		STORE RINT RIOA
		END
		"""
	loadProgram(p,asm,verbose)
	run(p,verbose)
	if verbose:
		print(p.ioa)
	assert(getIntFromBoolList(p.pinset.state) & 0x0000FFFF == 0x5555)



if __name__ == '__main__' :
	verbose = False
	from sys import argv
	
	if "-h" in argv:
		print("""\
-v verbose
-t execute this test in particular ("test" at the start is optional)
-l list all available tests and abort""")
	
	if "-v" in argv:
		verbose = True

	p = V16alpha()
	
	funcs = []
	for i in locals().copy():
		if i[:4] == "test":
			funcs.append(i)
	
	if "-l" in argv:
		for i in funcs:
			print(i)
		exit()
	if "-t" in argv:
		n = argv[argv.index("-t")+1]
		if n[:4] != "test":
			n="test"+n
		funcs = [n]
		
	for f in funcs:
		try:
			if verbose:
				print("\n\n\n")
			locals()[f](p, verbose)
			status = "OK"
		except Exception as e:
			if verbose:
				from traceback import print_exc ; print_exc(limit=-1,chain=False)
			status = "FAIL"
		print(" {:^4} {}".format(status, f[4:]))
		reset(p)
