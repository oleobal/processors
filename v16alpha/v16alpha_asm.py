

conversionTable={
	"STORE":0xA0,
	"DLPR" :0xA1,
	"DSPR" :0xA2,
	"DLST" :0xA3,
	"DSST" :0xA4,
	"PUSH" :0xA5,
	"POP"  :0xA6,
	
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
	
	constants={}
	sanitizedAssembly=[]
	# first hunt for assembler instructions
	# and sanitize code
	lineno=0
	for line in assembly.splitlines():
		line = line.strip()
		if line == "" or line[0] == "#"  :
			continue
		try:
			line = line[:line.index("#")]
		except ValueError:
			pass
		
		if line[0] != ":":
			sanitizedAssembly.append(line.strip())
			lineno+=1
			continue
		line = line[1:]
		l = line.split()
		if l[0].upper() == "CONST":
			constants[l[1]] = l[2]
		
		# label
		elif l[0][-1] == ":":
			constants[l[0][:-1]] = str(lineno)
			sanitizedAssembly.append(line[line.index(":")+1:].strip())
			
		else:
			raise Exception("Assembler instruction without meaning: "+line[0])
		
		lineno+=1
	
	output = bytearray()
	for line in sanitizedAssembly:
		byteline = bytearray()
		line = line.split()
		for i in line :
			if i[0] == ":":
				i = constants[i[1:]]
				
			if i.upper() in conversionTable :
				byteline.append(conversionTable[i.upper()])
			else:
				i = int(i,0)
				if i < 0x9F:
					byteline.append(i)
		
		# padding
		while len(byteline) < INSTRUCTION_SIZE:
			byteline.append(0xFF)
		output+=(byteline)
	
	if sizeWarning is not None and len(output) > sizeWarning :
		from sys import stderr
		print("Warning : program is over {} bytes !".format(sizeWarning), file=stderr)
	return output
