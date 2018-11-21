"""
Contains general concepts useful for all implementations
"""

class Register:
	"""
	A set of exposed pins, for I/O
	Pins function in a boolean way
	They can be set together, or addressed individually
	Append register pointers to the register field to update them when
	the pinset changes
	
	it is built around an bool list, so using the "state" field (which takes or
	returns a bool list) is preferable to using "value" (integer)
	"""
	
	def __str__(self):
		return "Reg {:<10} {:>3} bits {:<12}".format(self.name, len(self.pins), getStrFromBoolList(self.state))
	def __repr__(self):
		return "{} {} bits {}".format(self.name, len(self.pins), getStrFromBoolList(self.state))
	def __format__(self, spec):
		if spec=="indic":
			# indicators for subsets
			arrows=""
			for i in self.pins:
				if type(i) is bool:
					arrows+="|"
				elif i[1] == 0:
					arrows+="^"
				else:
					arrows+=" "
			return "Reg {:<10} {:>3} bits {:<12}\n{:>23} {:<12}".format(self.name, len(self.pins), getStrFromBoolList(self.state), "", arrows)
		else :
			return self.__str__()
	
	def __init__(self, numberOfPins, name="", overflow=True):
		"""
		if overflow is true, the register will silently overflow or underflow
		when given values too big or too small
		"""
		self.name = name
		self.size = numberOfPins
		self.maxValue = 2**numberOfPins -1
		self.doesOverflow=overflow
		self.pins = [False]*numberOfPins
		
		self.subscribers=[]
	

	
	def addSubscriber(self, object, functionToExecute, testFunction=lambda x:True, passPinset=False):
		"""
		:param functionToExecute: pointer to a function to be executed when the
		                          state of this changes
		:param testFunction: is passed the state, and the functionToExecute
		                     is only called if it returns true
							 
		:param passPinset: whether to pass a pointer to this pinset to the func
		"""
		self.subscribers.append((object, functionToExecute, testFunction, passPinset))
	
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
		0-indexed from the left
		"""
		if type(self.pins[index]) is bool:
			if self.pins[index] == newState:
				return
			self.pins[index] = newState
		else:
			if self.pins[index][0].getPinState(self.pins[index][1]) == newState:
				return
			self.pins[index][0].setPinState(self.pins[index][1], newState)
		for s in self.subscribers:
			if s[2](self.state):
				if (s[3]):
					s[1](s[0],self)
				else:
					s[1](s[0])
			
	
	def getPinState(self, index):
		"""
		get state for a single pin
		0-indexed from the left
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
			raise ValueError("Too many elements")
			
		
		for i in range(len(newState)):
			if type(self.pins[i]) is bool:
				self.setPinState(i,bool(newState[i]))
			else:
				self.pins[i][0].setPinState(self.pins[i][1], bool(newState[i]))
			
	@property
	def value(self):
		return getIntFromBoolList(self.state)
	@value.setter
	def value(self, newVal):
		if self.doesOverflow:
			while newVal < 0 or newVal > self.maxValue :
				if (newVal < 0):
					newVal += self.maxValue+1
				if (newVal > self.maxValue):
					newVal -= self.maxValue+1
		s = getBoolListFromInt(newVal)
		if len(s) > len(self.pins):
			raise ValueError("Value too large")
		self.state = s
	


	
def getIntFromBoolList(boollist, bigEndian=True):
	"""
	converts a list of bools into an int
	"""
	result = 0
	if not bigEndian:
		boollist.reverse()
	for i in range(len(boollist)):
		if boollist[i]:
			result+=1
		result<<=1
	result>>=1 # else it's one bit too much
	return result
	
def getBoolListFromInt(integer, bigEndian=True):
	"""
	converts an integer into a list of bools
	"""
	result=[]
	# TODO optimize
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
	:param groupBytesBy: will feed lines every (this) bytes
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
	
	
	maxLineNoDigits = max(2,len(str(len(outTable))))
	maxByteNoDigits = max(2,len(str(len(outTable)*groupBytesBy)))
	lineNoField = "{:<"+str(maxLineNoDigits)+"} {:>"+str(maxByteNoDigits)+"} "
	output += lineNoField.format("0", outTable[0][0])
	for j in outTable[0][1]:
		output+=" {:0>2X}".format(j)
	output+="\n"
	i = 1
	while i < len(outTable):
		if outTable[i][1] == outTable[i-1][1]:
			output += sameThingLine
		else:
			output += lineNoField.format(i, outTable[i][0])
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
