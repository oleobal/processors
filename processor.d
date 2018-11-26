/**
 * D version of common utilities
 */
import std.stdio;
import std.typecons;
import std.format;


/**
 * an register with a set number of bits
 * it over/underflows when the value is too high or too low
 * has properties "value" (integer) and "state" (array)
 */
class Register
{
	immutable string name;
	immutable int size;
	immutable ulong maxValue;
	/**
	 * first boolean : whether it part of a subregister
	 * if so, the last 2 values are used :
	 * we look up the value of (Register) at index (int)
	 * else the second bool holds the value
	 */
	Tuple!(bool, bool, Register, int)[] pins;
	Tuple!(void delegate(bool[]), bool function(bool[]))[] subscribers;
	// maybe it should be a delegate instead of just a function pointer
	// since it's typically going to be an object subscribing to something
	// I'm not sure
	
	this(int nbOfBits, string name="")
	{
		this.pins = [];
		for (int i = 0 ; i<nbOfBits ; i++) // I'm sure there's a better way..
			this.pins ~= [tuple(false, false, cast(Register)null, cast(int)null)]; 
		
		this.size = nbOfBits;
		int _maxValue = 1;
		for (int i = 1 ; i<nbOfBits ; i++)
		{ _maxValue<<=1; _maxValue+=1; }
		this.maxValue = _maxValue;
		this.name = name;
		
		//this.subscribers=[];
		
	}
	
	// https://wiki.dlang.org/Defining_custom_print_format_specifiers
	
	void toString(scope void delegate(const(char)[]) sink, FormatSpec!char fmt) const
	{
		switch(fmt.spec)
		{
			case 'm':
				sink(format("Reg %-10s %12s (%s,%04X)", this.name, getStringFromBoolList(this.state()), getNumberFromBoolList(this.state()), getNumberFromBoolList(this.state())));
				break;
			default:
				sink(format("%s %s (%s,%X)", this.name, getStringFromBoolList(this.state()), getNumberFromBoolList(this.state()), getNumberFromBoolList(this.state())));
				break;
		}
	}
	
	
	/**
	 * set the given register as a subset of the present register,
	 * at given index (indexed from 0 left to right)
	 */
	void setSubset(int index, Register register)
	{
		for (int i=0;i<register.pins.length;i++)
		{
			this.pins[index+i] = tuple(true, false, register, i);
		}
	}
	
	/**
	 * on state change, (B functionToExecute) will be executed with
	 * the state as argument, but only if (B condition) (given the state as well)
	 * returns true
	 */
	void addSubscriber(void delegate(bool[]) functionToExecute, bool function(bool[]) condition=function (bool[] b) => true)
	{
		this.subscribers~=[tuple(functionToExecute, condition)];
	}
	
	void setPinState(int index, bool value)
	{
		if (this.pins[index][0])
		{
			if (this.pins[index][2].getPinState(this.pins[index][3]) != value)
				return;
			this.pins[index][2].setPinState(this.pins[index][3], value);
		}
		else
		{
			if (this.pins[index][1] == value)
				return;
			this.pins[index][1] = value;
		}
		for (int i=0 ; i<this.subscribers.length;i++)
		{
			if (this.subscribers[i][1](this.state))
				this.subscribers[i][0](this.state);
		}
	}
	
	bool getPinState(int index) const
	{
		if (this.pins[index][0])
			return this.pins[index][2].getPinState(this.pins[index][3]);
		else
			return this.pins[index][1];
	}
	
	@property
	bool[] state() const
	{
		bool[] result=[];
		for (int i=0; i<this.size;i++)
			result~=[this.getPinState(i)];
		return result;
	}
	
	@property
	bool[] state(bool[] newState)
	{
		if (newState.length != this.size)
			throw new Exception("Parameter size (%s) is different from object size (%s).".format(newState.length, this.size));
		for (int i=0; i<this.size;i++)
		{
			this.setPinState(i, newState[i]);
		}
		return this.state;
	}
	
	// TODO value properties
	@property
	ulong value() const { return getNumberFromBoolList(this.state);}
	
	
	
	@property
	ulong value(ulong newVal)
	{ return getNumberFromBoolList(this.state(getBoolListFromNumber(newVal, this.size))); }
	
	
}

unittest /// basic register and sub-register functionality
{
	Register smallR = new Register(4);
	smallR.setPinState(0,true);
	smallR.setPinState(2,true);
	Register bigR = new Register(8);
	bigR.setPinState(1, true);
	bigR.setSubset(4,smallR);
	bigR.setPinState(7, true);
	//writeln(format("%m",bigR));
	assert(bigR.value == 0x4B);
	assert(smallR.value == 0xB);
	
	bigR.value = 0x55;
	assert(smallR.state == [false, true, false, true]);
	smallR.state = [true, true, true, false];
	assert(bigR.value == 0x5E);
	
}
unittest /// subscriber functionality
{
	class Something
	{
		int member;
		this()
		{
			this.member = 0;
		}
		void aFunction(bool[] input)
		{
			if ((getNumberFromBoolList(input) & 1) == 1)
				this.member+=1;
		}
		void anotherFunction(bool[] input)
		{
			this.member*=-1;
		}
	}

	Something s = new Something();
	Register r = new Register(4);
	r.addSubscriber(&(s.aFunction));
	r.state = [false, false, true, false];
	assert(s.member == 0);
	r.value= r.value + 1;
	assert(s.member == 1);
	
	// TODO SORT THIS OUT
}




/**
 * takes a big-endian list of bools and returns the corresponding integer
 * (up to 64 bits only)
 */
pure ulong getNumberFromBoolList(bool[] input)
{
	ulong result = 0;
	for (int i=0 ; i< input.length ; i++)
	{
		if (input[i])
			result+=1;
		result<<=1;
	}
	result>>=1;
	return result;
}
unittest
{
	// couldn't get a bool[] => ulong associative array to work, whatever
	bool[][] input =[
	[],
	[false],
	[true],
	[false, false, false, false, false], //  0
	[false, false, false, false, true ], //  1
	[false, true , false, true , false], // 10
	[true , false, false, false, false], // 16
	[true , false, true , false, true ], // 21
	[true , true , true , true , true ], // 31
	[true, true , true , true , true , true , true , true , true , true , true , true , true , true , true , true], // 65535
	];
	ulong[] output = [
	0,
	0,
	1,
	0,
	1,
	0b01010,
	0b10000,
	0b10101,
	0b11111,
	0xFFFF,
	];
	
	for (int i = 0 ; i < input.length ; i++)
	{
		assert(getNumberFromBoolList(input[i]) == output[i]);
	}
}

/**
 * takes an integer and returns a big-endian list of bools
 * It omits all leading zeroes by default
 * The (B length) argument can be used to specify a minimal length;
 * for instance, 0b010 would get turned into [t,f] with no length argument
 * but [f,f,t,f] with length=4
 */
pure bool[] getBoolListFromNumber(ulong input, int length=-1)
{
	ulong mask = 0x8000000000000000;
	bool skip = true ; // flag used to skip leading zeroes
	int count = 64; // used for the length argument
	bool[] result = [];
	
	while (mask > 0)
	{
		if (length == count)
			skip=!skip;
		
		if ((input & mask) == mask)
		{
			result~=[true];
			
			if (skip)
				skip = false;
		}
		else if (!skip)
			result~=[false];
		
		count--;
		mask>>=1;
	}
	return result;
}
unittest
{
	// couldn't get a bool[] => ulong associative array to work, whatever
	long[][] input = [
	[0, -1],
	[0,1],
	[1,-1],
	[0,5],
	[1,5],
	[0b01010,5],
	[0b10000,5],
	[0b10101,-1],
	[0b11111,-1],
	[0xFFFF,-1],
	];
	bool[][] output =[
	[],
	[false],
	[true],
	[false, false, false, false, false], //  0
	[false, false, false, false, true ], //  1
	[false, true , false, true , false], // 10
	[true , false, false, false, false], // 16
	[true , false, true , false, true ], // 21
	[true , true , true , true , true ], // 31
	[true, true , true , true , true , true , true , true , true , true , true , true , true , true , true , true], // 65535
	];
	
	for (int i = 0 ; i < input.length ; i++)
	{
		//writeln(input[i][0], " ", input[i][1], " ", output[i],  " | ", getBoolListFromNumber(cast(ulong)input[i][0], cast(int)input[i][1]));
		assert(getBoolListFromNumber(cast(ulong)input[i][0], cast(int)input[i][1]) == output[i]);
	}
}


pure string getStringFromBoolList(bool[] input)
{
	string result = "";
	foreach(bool b ; input)
	{
		if (b)
			result~="1";
		else
			result~="0";
	}
	return result;
}
unittest
{
	// couldn't get a bool[] => ulong associative array to work, whatever
	bool[][] input =[
	[],
	[false],
	[true],
	[false, false, false, false, false], //  0
	[false, false, false, false, true ], //  1
	[false, true , false, true , false], // 10
	[true , false, false, false, false], // 16
	[true , false, true , false, true ], // 21
	[true , true , true , true , true ], // 31
	[true, true , true , true , true , true , true , true , true , true , true , true , true , true , true , true], // 65535
	];
	string[] output = [
	"",
	"0",
	"1",
	"00000",
	"00001",
	"01010",
	"10000",
	"10101",
	"11111",
	"1111111111111111",
	];
	
	for (int i = 0 ; i < input.length ; i++)
	{
		//writeln(output[i], " | ", getStringFromBoolList(input[i]));
		assert(getStringFromBoolList(input[i]) == output[i]);
	}
}

void main() { } ;