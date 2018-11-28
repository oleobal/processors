/**
 *
 */
module v16alpha.v16alpha;

import std.stdio;
import std.math;

import processor;

struct instr
{
	string name;
	ubyte code;
	ushort time;
}

static struct instructions
{
	immutable instr[] list = [
		instr("STORE"	, 0xA0, 2),
		instr("DLPR"	, 0xA1, 3),
		instr("DSPR"	, 0xA2, 3),
		instr("DLST"	, 0xA3, 3),
		instr("DSST"	, 0xA4, 3),
		instr("PUSH"	, 0xA5, 2),
		instr("POP" 	, 0xA6, 2),
		instr("LABEL"	, 0xA7, 1),
		instr("JUMP"	, 0xA8, 1),
		
		
		instr("ADD" 	, 0xB0, 2),
		instr("REM" 	, 0xB1, 2),
		instr("MUL" 	, 0xB2, 3),
		instr("DIV" 	, 0xB3, 3),
		instr("MODU"	, 0xB4, 2),
		instr("AND" 	, 0xB5, 1),
		instr("OR"  	, 0xB6, 1),
		instr("XOR" 	, 0xB7, 1),
		
		instr("LSHIFT"	, 0xBA, 1),
		instr("RSHIFT"	, 0xBB, 1),
		
		instr("IFEQ"	, 0xC0, 2),
		instr("IFLT"	, 0xC1, 2),
		instr("IFLE"	, 0xC2, 2),
		instr("IFGT"	, 0xC3, 2),
		instr("IFGE"	, 0xC4, 2),
		instr("IFNE"	, 0xC5, 2),
		
		instr("END" 	, 0xCF, 1),
		
		
		instr("RINT" 	, 0xD0, 0),
		instr("RERR" 	, 0xD1, 0),
		instr("RIO" 	, 0xD2, 0),
		instr("PC"  	, 0xD3, 0), // program counter
		instr("SP"  	, 0xD4, 0), // stack pointer
		instr("RIOA" 	, 0xD5, 0),
		instr("RIOB" 	, 0xD6, 0),
		instr("RIOAL" 	, 0xD7, 0),
		instr("RIOAR" 	, 0xD8, 0),
		instr("RINTL" 	, 0xD9, 0),
		instr("RINTR" 	, 0xDA, 0),
		
		instr("LADD"	, 0xE0, 2),
		instr("LREM"	, 0xE1, 2),
		instr("LMUL"	, 0xE2, 3),
		instr("LDIV"	, 0xE3, 3),
		instr("LMODU"	, 0xE4, 3),
		instr("LAND"	, 0xE5, 1),
		instr("LOR" 	, 0xE6, 1),
		instr("LXOR"	, 0xE7, 1),
		instr("LSTORE"	, 0xE8, 1),
	];

	
	
	immutable instr[ubyte] byCode;
	immutable instr[string] byName;

	/**
	 * TODO In a perfect world these associative arrays over would be statically
	 * filled with Dlang's CTFE. 
	 * right now these functions do their own setup which is stupid
	 */
	 
	instr get(string name) const
	{
		if (byName.length == 0)
		{
			foreach (i ; list)
				byName[i.name] = i;
		}
		return byName[name];

	}
	instr get(ubyte  code) const
	{
		if (byCode.length == 0)
		{
			foreach (i ; list)
				byCode[i.code] = i;
		}
		return byCode[code];
	}
	
}




class V16alpha : Processor
{
	ulong cycleCount;
	ubyte[] program; 
	ubyte[] stack;
	// I'll be using dynamic arrays for convenience.. bound checking and all..
	// it also allows me to call the constructor multiple times, I hope
	
	Register programCounter;
	Register stackPointer;
	
	Register internal;
	Register internalL;
	Register internalR;
	
	Register io;
	Register ioa;
	Register ioaL;
	Register ioaR;
	Register iob;
	
	Register err;
	
	Register clock;
	Register progLoad;
	Register progCtrl;
	
	Register pinset;
	
	
	ubyte[] currentInstruction;
	int currentInstructionState;
	
	this()
	{
		cycleCount = 0;
		programCounter = new Register(8);
		program = [];
		// because the program counter is 1 byte, but addresses instructions, which are 3 bytes each
		for (int i=0;i<3*pow(2,8);i++)
			program~=[0xFF]; // TODO there might be a better way
		
		stackPointer = new Register(4);
		stack = [];
		for (int i=0;i<pow(2,4);i++)
			stack~=[0]; // TODO there might be a better way
		
		
		internal = new Register(16);
		internalL= new Register(8);
		internalR= new Register(8);
		internal.setSubset(0, internalL);
		internal.setSubset(8, internalR);
		
		ioa = new Register(16);
		ioaL= new Register(8);
		ioaR= new Register(8);
		ioa.setSubset(0, ioaL);
		ioa.setSubset(8, ioaR);
		io = ioa;
		iob = new Register(8);
		
		err = new Register(4);
		
		clock = new Register(1);
		progLoad = new Register(1);
		progCtrl = new Register(2);
		
		// I just realized.. why 32 pins ? DIP 40 seemed a lot more common.
		// oh well
		pinset = new Register(32);
		
		pinset.setSubset(0, clock);
		pinset.setSubset(1, err);
		pinset.setSubset(5, progLoad);
		pinset.setSubset(6, progCtrl);
		pinset.setSubset(8, iob);
		pinset.setSubset(16, ioa);
		
		
		currentInstruction = [0xFF, 0xFF, 0xFF];
		currentInstructionState = 0;
	}
	
	
	/**
	 * One processor cycle
	 * relies on state (currentInstruction, currentInstructionState..)
	 *
	 * triggered by turning the (I Clock) pin to 1 (it resets it to 0)
	 */
	void cycle()
	{
		clock.setPin(0, false);
		cycleCount++;
		
		
		
	}
}



unittest
{
	writeln("Hello");
	V16alpha p = new V16alpha();

	writeln(p.internal);
}
