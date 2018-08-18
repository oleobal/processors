

conversionTable={
	"STORE":0xA0,
	"DLPR" :0xA1,
	"DSPR" :0xA2,
	"DLST" :0xA3,
	"DSST" :0xA4,
	
	"ADD"  :0xB0,
	
	"END"  :0xCF,
	
	"RINT":0xD0,
	"RERR":0xD1,
	"RINO":0xD2,
	"RCNT":0xD3,
	"RSTA":0xD4,
}

INSTRUCTION_SIZE = 3

def assemble(assembly, sizeWarning=256):
	"""
	takes a string of assembly code and returns machine code
	for the V16alpha processor
	:param sizeWarning: issue a warning if the generated code is bigger
	                    set to None to disable
	"""
	output = bytearray()
	for line in assembly.splitlines():
		if line[0] == "#" :
			continue
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
	
	if sizeWarning is not None and len(output) > sizeWarning :
		from sys import stderr
		print("Warning : program is over {} bytes !".format(sizeWarning), file=stderr)
	return output
