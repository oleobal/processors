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
	
	g = 0; k=0
	output = "   0 "
	for i in array:
		g+=1
		k+=1
		output+=" {:0<2X}".format(i)
		if g==groupBytesBy:
			print(output)
			output = "{:>4} ".format(k)
			g=0
