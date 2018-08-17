from processor import *

class V16alpha(Processor)  :
	"""
	A simple processor
	Features :
	 - an unlimited program memory (list of instructions)
	 - a programCounter pointing at the current instruction
	 - one 16 bits register that overflows by resetting to 0
	 - and underflows by going to max value
	 - a stack with automatic operation (eg no manual counter)
	 - an IO 16-bits register presumably connected to a bus
	   (behaves like the internal register, but can be set by outside forces)
	 - an 8-bit register for status/error codes
	"""
	
	def __init__(self):
		self.cycleCount=0
		self.program = []
		self.programCounter= Register(16, name="COUNTER")
		self.register = Register(16, name="INTERNAL")
		self.stack = []
		self.io = Register(16, name="IO")
		self.status = Register(8, name="STATUS")
		# TODO catch exceptions and put them here instead
		
		self.instructionQueue=deque()
		# meant to keep a number of the state of each instruction in the
		# queue, to see at what state they are in
		self.instructionState=deque()
		# potentially, we could put multiple instructions in the queue and
		# execute them in parallel, if they are parallelizable
		# so basically it's some kind of potential pipeline
	

	
	def loadProgram(self,code):
		"""
		terminates current operations,
		replaces self.program with the given code,
		and resets programCounter to 0
		"""
		self.program = code
		self.programCounter=0
		self.status = 0
	
	
	def cycle(self):
		"""
		One processor cycle.
		"""
		if len(self.program) == 0:
			self.status.value = 1
			return
		if self.programCounter == len(self.program) :
			self.status.value = 2
			return
		


if __name__ == '__main__' :
	p = V16alpha()
	print(p.status)
	p.cycle()
	print(p.status)