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
	"END":1,
	"ADD":3,
	}
	
	errorCodes ={
	
	}
	
	# bits of addressing of the program table
	INSTRUCTION_ADDRESSING_SIZE = 8
	# octets per instruction
	INSTRUCTION_SIZE = 3
	
	def __init__(self):
		self.cycleCount=0
		self.program = bytearray([0xFF]*2**V16alpha.INSTRUCTION_ADDRESSING_SIZE*V16alpha.INSTRUCTION_SIZE)
		self.programCounter= Register(V16alpha.INSTRUCTION_ADDRESSING_SIZE, name="COUNTER")
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
			0xCF:"END",
			
			0xD0:self.register,
			0xD1:self.err,
			0xD2:self.io,
			0xD3:self.programCounter,
			0xD4:self.stackPointer,
			
			
			0xFF:0xFF
		}
		for i in range(0xA0):
			self.machineCode[i] = i

	def parseInstruction(self, counter):
		"""
		converts a byte array into a tuple
		(op[, target[, target]])
		:param counter: the current value of the program counter
		"""

		op = self.machineCode[self.program[counter*V16alpha.INSTRUCTION_SIZE]]
		t1 = self.machineCode[self.program[counter*V16alpha.INSTRUCTION_SIZE+1]]
		t2 = self.machineCode[self.program[counter*V16alpha.INSTRUCTION_SIZE+2]]
		
		if t1 == 0xFF :
			return [op]
		
		if t2 == 0xFF :
			return [op, t1]
			
		return [op, t1, t2]
	
	def loadProgram(self,code):
		"""
		terminates current operations,
		replaces self.program with the given code (after processing)
		and resets programCounter to 0
		
		:param code: a bytes object,
		             instructions of length 3 bytes, padded with 0xFF
		"""
		self.program = bytearray([0xFF]*2**V16alpha.INSTRUCTION_ADDRESSING_SIZE*V16alpha.INSTRUCTION_SIZE)
		
		i = 0
		for i in range(len(code)):
			self.program[i] = code[i]
		
		#printByteArray(self.program, groupBytesBy=3, name="v16alpha program")
		
		self.programCounter.value=0
		self.err.value = 0
	
	def loadNextInstruction(self):
		"""
		Loads next instruction from the program into the execution queue
		"""
		if len(self.program) == 0:
			self.err.value = 1
			return
		if self.programCounter.value == (2**V16alpha.INSTRUCTION_ADDRESSING_SIZE-1) :
			self.err.value = 9
			return
		try:
			instruction = self.parseInstruction(self.programCounter.value)
			
			op = instruction[0]
			if op == 0xFF:
				self.err.value = 3
				self.programCounter.value+=1
				return
		except KeyError :
			self.err.value = 11
			raise
		except Exception as e:
			self.err.value = 255 # dreaded
			raise
		
		if op not in V16alpha.operations:
			self.err.value = 10
			return
		
		self.instructionQueue.append(instruction)
		self.instructionState.append(V16alpha.operations[op])
			
	
	def cycle(self):
		"""
		One processor cycle.
		"""
		self.cycleCount += 1
		
		if self.err.value == 9:
			# starting execution back from the top
			self.programCounter.value = 0
			
		self.err.value = 2
		
		if (len(self.instructionQueue) == 0):
			try:
				self.loadNextInstruction()
			except Exception:
				if self.err.value == 2:
					self.err.value = 255
				raise
			if self.err.value == 3:
				return

		if self.instructionState[0] > 1 :
			self.instructionState[0]-=1
			return
			
		self.instructionState.popleft()
		instruction = self.instructionQueue.popleft()
		op = instruction[0]
		
		if op == "END":
			self.err.value=9
			return
		
		if op == "STORE":
			if len(instruction) != 3:
				self.err.value = 12
				return
			t1 = instruction[1]
			t2 = instruction[2]
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



