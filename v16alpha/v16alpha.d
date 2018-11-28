/**
 *
 */
module v16alpha.v16alpha;

import std.stdio;
import std.math;

import processor;

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
}



unittest
{
	writeln("Hello");
	V16alpha p = new V16alpha();

	writeln(p.internal);
}
