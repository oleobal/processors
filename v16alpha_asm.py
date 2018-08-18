

conversionTable={
	"STORE":0xA0,
	"DLPR":0xAA,
	"DSPR":0xA1,
	
	"END":0xCF,
	
	"RINT":0xD0,
	"RERR":0xD1,
	"RINO":0xD2,
	"RCNT":0xD3,
	"RSTA":0xD4,
}

INSTRUCTION_SIZE = 3

def compileASM(assembly):
	"""
	takes a string of assembly code and returns machine code
	for the V16alpha processor
	"""
	output = bytearray()
	for line in assembly.splitlines():
		byteline = bytearray()
		line = line.split()
		for i in line :
			if i in (conversionTable) :
				byteline.append(conversionTable[i])
			else:
				i = int(i,0)
				if i < 0x9F:
					byteline.append(i)
		#byteline.append([0xFF]*(INSTRUCTION_SIZE-len(byteline)))
		while len(byteline) < INSTRUCTION_SIZE:
			byteline.append(0xFF)
		output+=(byteline)
		
	return output