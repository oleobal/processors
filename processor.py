from collections import deque

class Register :
	"""
	A binary register with as many bits as you require
	"""
	
	def __str__(self):
		return "Register {0}, {1} bits, val {2} ({3})".format(self.name, self.size, self.value, hex(self.value))
	
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
