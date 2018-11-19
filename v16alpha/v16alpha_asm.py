

conversionTable={
	"STORE":0xA0,
	"DLPR" :0xA1,
	"DSPR" :0xA2,
	"DLST" :0xA3,
	"DSST" :0xA4,
	"PUSH" :0xA5,
	"POP"  :0xA6,
	"LABEL":0xA7,
	"JUMP" :0xA8,
	
	"ADD"  :0xB0,
	"REM"  :0xB1,
	"MUL"  :0xB2,
	"DIV"  :0xB3,
	"MODU" :0xB4,
	"AND"  :0xB5,
	"OR"   :0xB6,
	"XOR"  :0xB7,
	
	"IFEQ" :0xC0,
	"IFLT" :0xC1,
	"IFLE" :0xC2,
	"IFGT" :0xC3,
	"IFGE" :0xC4,
	
	"END"  :0xCF,
	
	"RINT" :0xD0,
	"RERR" :0xD1,
	"RINO" :0xD2,
	"RCNT" :0xD3,
	"RSTA" :0xD4,
	"RIOA" :0xD5,
	"RIOB" :0xD6,
	
	"LADD" :0xE0,
	"LREM" :0xE1,
	"LMUL" :0xE2,
	"LDIV" :0xE3,
	"LMODU":0xE4,
	"LAND" :0xE5,
	"LOR"  :0xE6,
	"LXOR" :0xE7,
	"LSTORE":0xE8
}

INSTRUCTION_SIZE = 3


ifSubstituteTable = {
	"=" : "EQ",
	"<" : "LT",
	"<=": "LE",
	">" : "GT",
	">=": "GE",
	"EQ": "EQ",
	"LT": "LT",
	"LE": "LE",
	"GT": "GT",
	"GE": "GE",
}
def lineSubstitute(instruction):
	"""
	turns constructs such as "if rint > 0" into "ifeq rint 0" (only one line)
	if the line does not start with if (then whitespace) it returns it unchanged
	"""
	i = instruction.split()
	if i[0].upper() != "IF":
		return instruction
	return "IF"+ifSubstituteTable[i[2].upper()]+" "+i[1]+" "+i[3]
	
	
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
			sanitizedAssembly.append(line)
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
		line = lineSubstitute(line)
		line = line.split()
		for i in line :
			if i[0] == ":":
				i = constants[i[1:]]
			
			if i.upper() in conversionTable :
				byteline.append(conversionTable[i.upper()])
			else:
				i = int(i,0)
				if i <= 0xFF:
					byteline.append(i)
				elif i <= 0xFFFF:
					byteline.append((i&0xFF00)>>8)
					byteline.append( i&0x00FF)
					# fill 2 bytes
				else:
					raise Exception("Literal over 0xFFFF : "+str(i))
					
		
		# arithmetic instructions
		if len(byteline) == 2 and 0xB0 <= byteline[0] <= 0xB7 :
			byteline.append(0)
			
		# padding
		while len(byteline) < INSTRUCTION_SIZE:
			byteline.append(0xFF)
		if len(byteline) != 3:
			raise Exception("Machine code instruction != 3 bytes : "+str(byteline))
		output+=(byteline)
	
	if sizeWarning is not None and len(output) > sizeWarning :
		from sys import stderr
		print("Warning : program is over {} bytes !".format(sizeWarning), file=stderr)
	return output
