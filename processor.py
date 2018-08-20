"""
Contains general concepts useful for all implementations
"""


class Register :
	"""
	A binary register with as many bits as you require
	"""
	
	def __str__(self):
		return "Reg {:<10} {:>3} bits val {:<6} (0x{:X})".format(self.name, self.size, self.value, self.value)
	
	def __init__(self, size, name=""):
		self.name = name
		self.size = size
		self.maxValue = 2**size -1
		self._value = 0
	
	@property
	def value(self):
		"""16 bits register"""
		return self._value
	@value.setter
	def value(self, newVal):
		while newVal < 0 or newVal > self.maxValue :
			if (newVal < 0):
				newVal += self.maxValue+1
			if (newVal > self.maxValue):
				newVal -= self.maxValue+1
		self._value = newVal
	@value.deleter
	def value(self):
		"""Please don't"""
		del self._value
		


class Pinset:
	"""
	A set of exposed pins, for I/O
	Pins function in a boolean way
	They can be set together, or addressed individually
	
	Pinsets also offer suscription features, to trigger things on change
	"""
	def __init__(self, numberOfPins):
		self._pins = [False]*numberOfPins
		self.executeOnChange = []
	
	def addSuscriber(self, functionToExecute, targetState=None, passState=False):
		"""
		:param functionToExecute: pointer to a function to be executed when the
		                          state of this changes
		:param targetState: only execute the function if the state of the
		                    pinset is the same as the table of bools given
		:param passState: whether to pass a copy of the bool table on execution
		"""
		self.executeOnChange+=[functionToExecute, targetState, passState]

	@property
	def pins(self):
		return self._pins
	@pins.setter
	def pins(self, newState):
		"""
		Set the new state of the pinset. Will alert suscribers.
		:param newState: either a list of bools or an int
		"""
		# TODO fix this, it's not really duck-typesque
		if type(newState) is int or type(newState) is bool:
			newState = getBoolListFromInt(newState)

		if len(newState) != len(self.pins):
			raise TypeError("Wrong number of elements")
			
		for i in range(len(newState)):
			self._pins[i] = bool(newState[i])
		
		# notify each suscriber
		# TODO
		
	@pins.deleter
	def pins(self):
		del self._pins

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
	i=1
	while 2**i < integer:
		i+=1
	i-=1
	while i >= 0 :
		if integer-2**i >= 0 :
			integer-=2**i
			result.append(True)
		else:
			result.append(False)
		i-=1
	
	if bigEndian==False :
		result.reverse()
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
