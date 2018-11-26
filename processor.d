/**
 * D version of common utilities
 */
import std.stdio;


/**
 * an register with a set number of bits
 * it over/underflows when the value is too high or too low
 * has properties "value" (integer) and "state" (array)
 */
class Register
{
	// TODO investigate whether using a BitArray would be better
	// for performance (size benefits being irrelevant)
	string name;
	int size;
	ulong maxValue;
	bool[] pins;
	this(int nbOfBits, string name="")
	{
		this.pins = new bool[nbOfBits]; // bool.init == false
		this.size = nbOfBits;
		this.maxValue = 1;
		for (int i = 1 ; i<nbOfBits ; i++)
		{ maxValue<<=1; maxValue+=1; }
		this.name = name;
		
	}
	
	@property
	ulong value() { return getNumberFromBoolList(this.pins);}
	/+
	@property
	ulong value(ulong newVal)
	{
		
	}
	+/
	
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