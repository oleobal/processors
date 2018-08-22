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
	 - a 5-bit register for status/error codes
	"""
	

	# cost of ops in cycles
	# of course this is nonsensical, especially if I want to implement
	# a pipeline some day
	# but really this whole thing is nonsensical
	
	operations={
	"STORE":2,
	"DLPR" :3,
	"DSPR" :3,
	"DLST" :3,
	"DSST" :3,
	"PUSH" :2,
	"POP"  :2,

	"ADD"  :2,
	
	"END"  :1,
	   0xFF:1,
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
		self.stackPointer = Register(4, name="STACK")
		self.stack = bytearray([0x00]*2**self.stackPointer.size)
		self.io = Register(16, name="IO")
		self.err = Register(5, name="ERROR")
		# TODO catch exceptions and put them here instead
		
		self.currentInstruction  = bytearray([0xFF]*V16alpha.INSTRUCTION_SIZE)
		self.currentInstructionDecoded = None
		# meant to keep a number of the state of each instruction in the
		# queue, to see at what state they are in
		self.currentInstructionState = 0
		# removed the queue mechanism.. Maybe in a next gveneration.
		# I want this to be more realistic
	
	
		# translation table
		# I could pull this automatically and stick it in the documentation,
		# yes.. But it wouldn't be in line with the spirit of the whole
		# thing.
		
		# the reason this is here is the pointers to local methods.
		self.machineCode={
			0xA0:"STORE",
			0xA1:"DLPR",
			0xA2:"DSPR",
			0xA3:"DLST",
			0xA4:"DSST",
			0xA5:"PUSH",
			0xA6:"POP",
			
			0xB0:"ADD",
			
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

	def retrieveInstruction(self, counter):
		"""
		(no side effects)
		retrieves the instruction at (counter) in the program memory
		returns a bytearray of length 3
		"""
		# doesn't work well with just [i:i+2x] addressing syntax
		out = bytearray()
		i = 0
		while i < V16alpha.INSTRUCTION_SIZE:
			out.append(self.program[counter*V16alpha.INSTRUCTION_SIZE+i])
			i+=1
			
		return out
		
	def parseInstruction(self, array):
		"""
		(no side effects)
		converts a byte array into a list
		[op[, target[, target]]]
		:param counter: the current value of the program counter
		"""

		op = self.machineCode[array[0]]
		t1 = self.machineCode[array[1]]
		t2 = self.machineCode[array[2]]
		
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
		Loads next instruction from the program into the current
		execution data unit
		"""
		if self.programCounter.value == (2**V16alpha.INSTRUCTION_ADDRESSING_SIZE-1) :
			self.err.value = 9
			return
		try:
			machineInstr = self.retrieveInstruction(self.programCounter.value)
			instruction = self.parseInstruction(machineInstr)
			
			
		except KeyError :
			self.err.value = 11
			raise
		except Exception as e:
			self.err.value = 255 # dreaded
			raise
		
		if instruction[0] not in V16alpha.operations:
			self.err.value = 10
			return
		
		self.currentInstruction = machineInstr
		self.currentInstructionDecoded = instruction
		self.currentInstructionState = V16alpha.operations[instruction[0]]
		
	
	def cycle(self):
		"""
		One processor cycle.
		"""
		self.cycleCount += 1
		
		if self.err.value == 9:
			# starting execution back from the top
			self.programCounter.value = 0
			
		
		
		if self.currentInstructionState == 0:
			try:
				if self.err.value != 0:
					self.programCounter.value+=1
				
				self.loadNextInstruction()
				
			except Exception:
				if self.err.value == 2:
					self.err.value = 31
				raise
			if self.err.value in (3, 9):
				return

		self.err.value = 2
		
		self.currentInstructionState-=1
		if self.currentInstructionState > 0 :
			return
		
		instruction = self.currentInstructionDecoded
		op = instruction[0]
		
		
		if op == 0xFF:
			self.err.value=3
			return

		elif op == "END":
			self.err.value=9
			return
		
		elif op == "STORE":
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

		elif op in ("DLPR", "DLST") :
			if len(instruction) != 3:
				self.err.value = 12
				return
			if op == "DLPR":
				dataArray = self.program
			elif op == "DLST":
				dataArray = self.stack
			index = instruction[1]
			target = instruction[2]
			if type(index) is int:
				a = dataArray[index]
			elif type(index) is Register:
				a = dataArray[index.value]
			
			if type(target) is Register:
				target.value = a
			else:
				self.err.value = 12
				return
			
		
		elif op in ("DSPR", "DSST") :
			if len(instruction) != 3:
				self.err.value = 12
				return
			if op == "DSPR":
				dataArray = self.program
			elif op == "DSST":
				dataArray = self.stack
			source = instruction[1]
			index = instruction[2]
			if type(source) is int:
				a = source
			elif type(source) is Register:
				a = source.value
			if type(index) is int:
				dataArray[index] = a
			elif type(index) is Register:
				dataArray[index.value] = a

		elif op == "PUSH" :
			if len(instruction) != 2:
				self.err.value = 12
				return
			source = instruction[1]
			if type(source) is int :
				self.stack[self.stackPointer.value] = source
			elif type(source) is Register:
				self.stack[self.stackPointer.value] = source.value
			self.stackPointer.value+=1
		
		elif op == "POP":
			if len(instruction) != 2:
				self.err.value = 12
				return
			target = instruction[1]
			if type(target) is Register:
				self.stackPointer.value-=1
				target.value = self.stack[self.stackPointer.value]
			else:
				self.err.value=12
				return
			

		elif op == "ADD":
			if len(instruction) != 3:
				self.err.value = 12
				return
			source = instruction[1]
			target = instruction[2]
			if type(source) is int:
				a = source
			elif type(source) is Register:
				a = source.value
			if type(target) is Register:
				target.value += a
			else:
				self.err.value = 12
				return
		
		self.err.value = 4

		
