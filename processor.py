from collections import deque

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
		print(name)
	
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
		output+=" {:0<2X}".format(j)
	output+="\n"
	i = 1
	while i < len(outTable):
		if outTable[i][1] == outTable[i-1][1]:
			output += sameThingLine
		else:
			output += "{:>4}".format(outTable[i][0])
			for j in outTable[i][1]:
				output+=" {:0<2X}".format(j)
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
