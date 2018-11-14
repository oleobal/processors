"""
Contains general concepts useful for all implementations
"""


class Register :
	"""
	A binary register with as many bits as you require
	"""
	
	def __str__(self):
		return "Reg {:<10} {:>3} bits {:<6} (0x{:X})".format(self.name, self.size, self.value, self.value)
	def __repr__(self):
		return "Reg {} {} bits {} (0x{})".format(self.name, self.size, self.value, self.value)
	
	def __init__(self, size, name=""):
		self.name = name
		self.size = size
		self.maxValue = 2**size -1
		self._value = 0
		"""
		pinsets to be updated when this register's value changes
		"""
		self.pinsets = []
	
	@property
	def value(self):
		return self._value
	@value.setter
	def value(self, newVal):
		# should this test be after the over/underflow calculations ?
		if newVal == self._value:
			return
		while newVal < 0 or newVal > self.maxValue :
			if (newVal < 0):
				newVal += self.maxValue+1
			if (newVal > self.maxValue):
				newVal -= self.maxValue+1
		self._value = newVal
		for p in self.pinsets:
			p.state = self._value


class Pinset:
	"""
	A set of exposed pins, for I/O
	Pins function in a boolean way
	They can be set together, or addressed individually
	Append register pointers to the register field to update them when
	the pinset changes
	"""
	
	def __str__(self):
		# indicators for subsets
		arrows=""
		for i in self.pins:
			if type(i) is bool:
				arrows+="|"
			elif i[1] == 0:
				arrows+="^"
			else:
				arrows+=" "
		return "Pin {:<10} {:>3} pins {:<12}\n{:>23} {:<12}".format(self.name, len(self.pins), getStrFromBoolList(self.state), "", arrows)
	def __repr__(self):
		return "{} {} pins {}".format(self.name, len(self.pins), getStrFromBoolList(self.state))
	
	def __init__(self, numberOfPins, name=""):
		self.name = name
		self.pins = [False]*numberOfPins
		# registers to change when this changes
		self.registers = []
	

	def setSubset(self, index, set):
		"""
		replace a number of pins by another Pinset
		in the _pins table the corresponding pins will be replaced by pointers
		to that Pinset
		:param index: the index to place this pinset at
		:param set: the pinset
		"""
		for i in range(len(set.pins)):
			self.pins[i+index] = [set, i]
		
	def setPinState(self, index, newState):
		"""
		set state for a single pin
		"""
		if type(self.pins[index]) is bool:
			if self.pins[index] == newState:
				return
			self.pins[index] = newState
		else:
			if self.pins[index][0].getPinState(self.pins[index][1]) == newState:
				return
			self.pins[index][0].setPinState(self.pins[index][1], newState)
		for r in self.registers:
			r.value = getIntFromBoolList(self.state)
	
	def getPinState(self, index):
		"""
		get state for a single pin
		"""
		p = self.pins[index]
		if type(p) is bool:
			return p
		else:
			return p[0].getPinState(p[1])
	
	
	@property
	def state(self):
		result = []
		for p in self.pins:
			if type(p) is bool:
				result.append(p)
			else:
				result.append(p[0].getPinState(p[1]))
		return result
		
	@state.setter
	def state(self, newState):
		"""
		Set the new state of the pinset.
		:param newState: either a list of bools or an int
		"""
		if type(newState) is int or type(newState) is bool:
			newState = getBoolListFromInt(newState)

		# pad the front of the list
		while len(newState) < len(self.pins):
			newState = [False]+newState
		
		if len(newState) > len(self.pins):
			raise TypeError("Too many elements")
			
		
		for i in range(len(newState)):
			if type(self.pins[i]) is bool:
				self.setPinState(i,bool(newState[i]))
			else:
				self.pins[i][0].setPinState(self.pins[i][1], bool(newState[i]))
			
	
def link(register, pinset):
	"""
	helper function to link a register and a pinset together
	(changing the value of one changes the value of the other)
	"""
	# add code to check for duplicates, maybe ?
	register.pinsets.append(pinset)
	pinset.registers.append(register)

def createLinkedRegAndPinset(size, name=""):
	"""
	helper function that creates a register and pinset of same size and name,
	links them, and returns a tuple (r,p)
	"""
	r = Register(size, name)
	p = Pinset(size, name)
	link(r,p)
	return (r,p)
	
def createLinkedPinsetFromReg(register):
	"""
	helper function that creates a pinset from a register (same size and name),
	links them, and returns the pinset
	"""
	p = Pinset(register.size, register.name)
	link(register, p)
	return p




	
def getIntFromBoolList(boollist, bigEndian=True):
	"""
	converts a list of bools into an int
	Don't fight me, please
	"""
	result = 0
	if bigEndian:
		boollist.reverse()
	for i in range(len(boollist)):
		result+=boollist[i]*2**i
	# TODO there's probably a way to do it without computation..
	return result
	
def getBoolListFromInt(integer, bigEndian=True):
	"""
	converts an integer into a list of bools
	"""
	# this is even worse than the other function, god
	result=[]
	integer = bin(integer)[2:]
	for i in range(len(integer)):
		if integer[i] == "1":
			result.append(True)
		else:
			result.append(False)
		i-=1
	
	if bigEndian==False :
		result.reverse()
	return result

def getStrFromBoolList(boollist):
	result=""
	for b in boollist:
		if b:
			result+="1"
		else:
			result+="0"
	return result
	
	
class Processor :
	pass

def printByteArray(array, groupBytesBy=8, name=None):
	"""
	Utility for printing byte arrays, in hexadecimal
	:param array: the bytes() or bytearray()
	:param groupBytesBy: will skip lines every (this) bytes
	:param name: will print that at the top
	"""
	if name != None:
		print(name, ":")
	
	outTable = []
	
	i = 0
	while i < len(array):
		g = 0
		thisGroup = (i, bytearray())
		while g < groupBytesBy:
			thisGroup[1].append(array[i])
			i+=1
			g+=1
		outTable.append(thisGroup)
	
	lineLength = 5+3*groupBytesBy
	sameThingLine = " "*(lineLength//4)+"[same]\n"
	output = ""
	
	output += "{:>4}".format(outTable[0][0])
	for j in outTable[0][1]:
		output+=" {:0>2X}".format(j)
	output+="\n"
	i = 1
	while i < len(outTable):
		if outTable[i][1] == outTable[i-1][1]:
			output += sameThingLine
		else:
			output += "{:>4}".format(outTable[i][0])
			for j in outTable[i][1]:
				output+=" {:0>2X}".format(j)
			output+="\n"
		i+=1
	
	
	
	lines =  output.splitlines(keepends=True)
	output = ""
	i = 0
	sameCount = 0
	while i < len(lines):
		if lines[i] == sameThingLine:
			sameCount+=1
		else:
			if sameCount == 1:
				output+=sameThingLine
			elif sameCount > 1 :
				output+=sameThingLine[:-1]+" x"+str(sameCount)+"\n"
			output+=lines[i]
			sameCount=0
		i+=1
	
	if sameCount == 1:
		output+=sameThingLine
	elif sameCount > 1 :
		output+=sameThingLine[:-2]+" x"+str(sameCount)+"]\n"
	
	print(output)
