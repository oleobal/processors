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
	"STORE" :2,
	"DLPR"  :3,
	"DSPR"  :3,
	"DLST"  :3,
	"DSST"  :3,
	"PUSH"  :2,
	"POP"   :2,
	"LABEL" :1,
	"JUMP"  :1,

	"ADD"   :2,
	"REM"   :2,
	"MUL"   :3,
	"DIV"   :3,
	"MODU"  :2,
	"AND"   :1,
	"OR"    :1,
	"XOR"   :1,
	
	"LSHIFT":1,
	"RSHIFT":1,
	
	"IFEQ"  :2,
	"IFLT"  :2,
	"IFLE"  :2,
	"IFGT"  :2,
	"IFGE"  :2,
	
	"END"   :1,
	
	
	"LADD"  :2,
	"LREM"  :2,
	"LMUL"  :3,
	"LDIV"  :3,
	"LMODU" :2,
	"LAND"  :1,
	"LOR"   :1,
	"LXOR"  :1,
	"LSTORE":1,



	 0xFF   :1,
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
		self.ioa = Register(16, name="I/O A")
		self.iob = Register(8,  name="I/O B")
		self.io = self.ioa
		self.err = Register(4, name="ERROR")
		# TODO catch exceptions and put them here instead
		
		self.pinset = Register(32, "V16alpha")
		
		self.clockPin = Register(1, "Clock")
		def handleClockUp(self, clockPinset):
			clockPinset.setPinState(0, False)
			self.cycle()
		self.clockPin.addSubscriber(self, handleClockUp, lambda x: x==[True], True)
		
		self.pinset.setSubset(0, self.clockPin)
		self.pinset.setSubset(1, self.err)
		
		# prog load is not subscribed to because we only check it when an
		# instruction is finished
		self.progLoadPin = Register(1, "Prog load")
		self.pinset.setSubset(5, self.progLoadPin)
		self.progCtrlPin = Register(2, "Prog ctrl")
		
		self.pinset.setSubset(6, self.progCtrlPin)
		self.pinset.setSubset(8, self.iob)
		self.pinset.setSubset(16, self.ioa)
		
		self.currentInstruction  = bytearray([0xFF]*V16alpha.INSTRUCTION_SIZE)
		self.currentInstructionDecoded = None
		self.currentInstructionState = 0
	
		self.resetState = 5
		self.labelSeek = -1 # -1 if no label is being jumped to
		
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
			0xA7:"LABEL",
			0xA8:"JUMP",
			
			0xB0:"ADD",
			0xB1:"REM",
			0xB2:"MUL",
			0xB3:"DIV",
			0xB4:"MODU",
			0xB5:"AND",
			0xB6:"OR",
			0xB7:"XOR",
			
			0xBA:"LSHIFT",
			0xBB:"RSHIFT",
			
			0xC0:"IFEQ",
			0xC1:"IFLT",
			0xC2:"IFLE",
			0xC3:"IFGT",
			0xC4:"IFGE",
			
			0xCF:"END",
			
			0xD0:self.register,
			0xD1:self.err,
			0xD2:self.io,
			0xD3:self.programCounter,
			0xD4:self.stackPointer,
			0xD5:self.ioa,
			0xD6:self.iob,
			
			0xE0:"LADD",
			0xE1:"LREM",
			0xE2:"LMUL",
			0xE3:"LDIV",
			0xE4:"LMODU",
			0xE5:"LAND",
			0xE6:"LOR",
			0xE7:"LXOR",
			0xE8:"LSTORE",
			
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
		if op in ["JUMP", "LABEL", "LADD", "LREM", "LMUL", "LDIV", "LMODU", "LAND", "LOR", "LXOR", "LSTORE"]:
			a = array[1]<<8
			a +=array[2]
			return [op, a]
		t1 = self.machineCode[array[1]]
		t2 = self.machineCode[array[2]]
	
			
		if t1 == 0xFF :
			return [op]
		
		if t2 == 0xFF :
			return [op, t1]
			
		return [op, t1, t2]
	
	def loadProgram(self,code):
		"""
		DEBUG
		
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
			self.err.value = 15 # dreaded
			raise
		
		if instruction[0] not in V16alpha.operations:
			self.err.value = 10
			return
		
		self.currentInstruction = machineInstr
		self.currentInstructionDecoded = instruction
		self.currentInstructionState = V16alpha.operations[instruction[0]]
		
	
	def loadInstrIntoProg(self):
		"""
		loads an instruction from IOA to program memory
		"""
		self.progLoadPin.setPinState(0, False)
		addr = (self.ioa.value & 0xFF00) // 256
		addr = addr*3 + getIntFromBoolList(self.progCtrlPin.state)
		op   = self.ioa.value & 0x00FF
		self.program[addr] = op
		self.currentInstructionState = 3
		self.err.value = 5
		
		
	
	def cycle(self):
		"""
		One processor cycle.
		"""
		self.cycleCount += 1

		if self.err.value == 9:
			# starting execution back from the top
			self.programCounter.value = 0
			
		
		if self.currentInstructionState < 0:
			raise Exception("Grave instruction processing failure")
			# there are two lists of instructions in this file,
			# maybe I forgot to put it in one ?
		
		if self.currentInstructionState == 0:
			# check whether we are to load instructions
			if self.progLoadPin.getPinState(0) == True:
				if self.progCtrlPin.state == [True, True]:
					self.resetState-=1
					self.programCounter.value = 0
					self.err.value = 0
					if self.resetState == 0:
						
						self.__init__()
						
					
				else:
					self.resetState = 5
					self.loadInstrIntoProg()
				self.progLoadPin.setPinState(0, False)
				self.progCtrlPin.state = [False, False]
				return
			
			self.resetState = 5

			try:
				if self.err.value != 0:
					self.programCounter.value+=1
				
				self.loadNextInstruction()
				
			except Exception:
				if self.err.value == 2:
					self.err.value = 15
				raise
			if self.err.value in (3, 9):
				return

		self.err.value = 2
		
		self.currentInstructionState-=1
		if self.currentInstructionState > 0 :
			return
			
		# execution not started
		if self.currentInstructionDecoded == None :
			self.err.value = 0
			return
		
		instruction = self.currentInstructionDecoded
		op = instruction[0]
		
		
		if (self.labelSeek >= 0):
			if op == "LABEL" and instruction[1] == self.labelSeek :
				self.labelSeek = -1
			else:
				self.err.value=3
				return
				
		
		elif op == 0xFF or op == "LABEL" :
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
		
		elif op == "JUMP":
			if len(instruction) != 2:
				self.err.value = 12
				return
			self.labelSeek = instruction[1]
				

		elif op in ["ADD", "REM", "MUL", "DIV", "MODU", "AND", "OR", "XOR"]:
			if len(instruction) == 3:
				if type(instruction[1]) is int:
					a = instruction[1]
				elif type(instruction[1]) is Register:
					a = instruction[1].value
					
				if type(instruction[2]) is int:
					b = instruction[2]
				elif type(instruction[2]) is Register:
					b = instruction[2].value
			else:
				self.err.value = 12
				return
			
			t = self.register
			
			if b==0 and type(instruction[2]) is int:
				b = a
				a = t.value
			
			try:
				if op == "ADD":
					t.value = a+b
				elif op == "REM":
					t.value = a-b
				elif op == "MUL":
					t.value = a*b
				elif op == "DIV":
					t.value = a//b
				elif op == "MODU":
					t.value = a%b
				
				elif op == "AND" :
					t.value = a&b
				elif op == "OR" :
					t.value = a|b
				elif op == "XOR" :
					t.value = a^b
			except Exception:
				self.err.value = 13
				return
		
		elif op in ["LSHIFT", "RSHIFT"]:
			if len(instruction) != 3:
				self.err.value = 12
				return
			if type(instruction[2]) is int:
				a = instruction[2]
			else:
				a = instruction[2].value
			if op == "LSHIFT":
				instruction[1].value <<= a
			elif op == "RSHIFT":
				instruction[1].value >>= a
		
		# 2-byte ops
		elif op in ["LSTORE", "LADD", "LREM", "LMUL", "LDIV", "LMODU", "LAND", "LOR", "LXOR"]:
			if op == "LSTORE":
				self.register.value = instruction[1]
			if op == "LADD":
				self.register.value += instruction[1]
			if op == "LREM":
				self.register.value -= instruction[1]
			if op == "LMUL":
				self.register.value *= instruction[1]
			if op == "LDIV":
				self.register.value //= instruction[1]
			if op == "LMODU":
				self.register.value %= instruction[1]
			if op == "LAND":
				self.register.value &= instruction[1]
			if op == "LOR":
				self.register.value |= instruction[1]
			if op == "LXOR":
				self.register.value ^= instruction[1]
		
		
		
		elif op in ["IFEQ", "IFLT", "IFLE", "IFGT", "IFGE"]:
			if len(instruction) == 3:
				if type(instruction[1]) is int:
					a = instruction[1]
				elif type(instruction[1]) is Register:
					a = instruction[1].value
					
				if type(instruction[2]) is int:
					b = instruction[2]
				elif type(instruction[2]) is Register:
					b = instruction[2].value
			else:
				self.err.value = 12
				return
			try:
				if op == "IFEQ":
					if a != b:
						self.programCounter.value+=1
				if op == "IFLT":
					if a >= b:
						self.programCounter.value+=1
				if op == "IFLE":
					if a > b:
						self.programCounter.value+=1
				if op == "IFGT":
					if a <= b:
						self.programCounter.value+=1
				if op == "IFGE":
					if a < b:
						self.programCounter.value+=1
			except Exception:
				self.err.value = 15
				return
				
		
		self.err.value = 4

		
