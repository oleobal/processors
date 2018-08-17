from processor import *



class V16alpha(Processor)  :
	"""
	A simple processor
	Features :
	 - an unlimited program memory (list of instructions)
	 - a 16-bits programCounter register pointing at the current instruction
	 - one general purpose 16 bits register
	 - a stack with automatic operation (eg no manual counter)
	 - an IO 16-bits register presumably connected to a bus
	   (behaves like the internal register, but can be set by outside forces)
	 - an 8-bit register for status/error codes
	"""
	

	# cost of ops in cycles
	# of course this is nonsensical, especially if I want to implement
	# a pipeline some day
	# but really this whole thing is nonsensical
	
	operations={
	"STORE":2,
	"ADD":3
	}
	
	def __init__(self):
		self.cycleCount=0
		self.program = []
		self.programCounter= Register(16, name="COUNTER")
		self.register = Register(16, name="INTERNAL")
		self.stack = [] #TODO stack structure
		self.stackPointer = Register(4, name="STACK")
		self.io = Register(16, name="IO")
		self.err = Register(8, name="ERROR")
		# TODO catch exceptions and put them here instead
		
		self.instructionQueue=deque()
		# meant to keep a number of the state of each instruction in the
		# queue, to see at what state they are in
		self.instructionState=deque()
		# potentially, we could put multiple instructions in the queue and
		# execute them in parallel, if they are parallelizable
		# so basically it's some kind of potential pipeline
	
	
		# translation table
		# I could pull this automatically and stick it in the documentation,
		# yes.. But it wouldn't be in line with the spirit of the whole
		# thing.
		
		# the reason this is here is the pointers to local methods.
		self.machineCode={
			0xA0:"STORE",
			
			0xD0:self.register,
			0xD1:self.err,
			0xD2:self.io,
			0xD3:self.programCounter,
			0xD4:self.stackPointer

		}
		for i in range(0xA0):
			self.machineCode[i] = i

	def parseInstruction(self, code):
		"""
		converts a byte array into a tuple
		(op, target[, target])
		"""
		op = self.machineCode[code[0]]
		t1 = self.machineCode[code[1]]
		if len(code) == 2:
			return (op, t1)
		else:
			t2 = self.machineCode[code[2]]
			return (op, t1, t2)
	
	def loadProgram(self,code):
		"""
		terminates current operations,
		replaces self.program with the given code (after processing)
		and resets programCounter to 0
		
		:param code: a bytes object,
		             instructions separated by 0xFF
		"""
		self.program=[]
		
		code = code.split(bytes([0xFF]))
		for i in code:
			if i == b'':
				continue
			self.program.append(i)
		
		self.programCounter.value=0
		self.err.value = 0
	
	
	def cycle(self):
		"""
		One processor cycle.
		"""
		self.cycleCount += 1
		self.err.value = 2
		
		
		if len(self.program) == 0:
			self.err.value = 1
			return
		if self.programCounter.value == len(self.program) :
			self.err.value = 3
			return
		
		try:
			instruction = self.parseInstruction(self.program[self.programCounter.value])
			
			op = instruction[0]
			t1 = instruction[1]
			if len(instruction) > 2 :
				t2 = instruction[2]
		except KeyError :
			self.err.value = 11
			return
		except Exception as e:
			self.err.value = 255 # dreaded
			raise
		
		if op not in V16alpha.operations:
			self.err.value = 10
			return

		
		if op == "STORE":
			if len(instruction) != 3:
				self.err.value = 12
				return
			if type(t1) is int :
				a = t1
			elif type(t1) is Register:
				a = t1.value
			
			
			try:
				t2.value = a
			except Exception:
				self.err.value = 11
				return





		
		self.programCounter.value+=1


if __name__ == '__main__' :
	p = V16alpha()
	print(p.err)
	p.cycle()
	print(p.err)
	print(p.register)
	p.loadProgram(bytes([0xA0, 0x0A, 0xD0, 0xFF]))
	while (p.err.value < 3):
		p.cycle()
		print(p.register)
		print(p.err)
