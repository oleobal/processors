### Fantasy processor(s)

This repository is meant to be a collection of emulated components. I'm only looking to emulate a vague abstraction of the interface, not the actual electrical workings.

The only one as of now is the V16alpha. Files :

 - `v16alpha/v16alpha.md` contains [the manual](v16alpha/v16alpha.md)
 - `v16alpha/v16alpha.py` contains the actual processor as a class
 - `v16alpha/v16alpha_asm.py` contains the assembler
 - `v16alpha_test.py` can be executed to test the processor

#### An example

The assembly code :
```
STORE 12  RIOA
STORE 157 RINT
ADD 50
DSPR RINT RIOA
```

Seeks to place `0xCF`, the end instruction, into the program memory of the processor to end execution. It cannot do so directly, because V16alpha machine code uses byte words where everything above `0x9F` is reserved, and everything beneath is a numeric literal. So it stores 157 into the I/O register (used as general purpose here), and adds 50 to it to compute the end instruction, before writing it at index 12 in the program memory.

Annotated version :
```
STORE 12  RIOA # Store 12 in I/O register A (there are 2, A and B)
STORE 157 RINT # RINT is the internal register
ADD 50         # RINT is also where arithmetic operations take place (accumulator)
DSPR RINT RIOA # Store the value in RINT (207 == 0xCF)in the program memory at index RIOA (12)
```


Execution :
```
Reg ERROR        4 bits 2      (0x2) Reg COUNTER      8 bits 0      (0x0)
Reg ERROR        4 bits 4      (0x4) Reg COUNTER      8 bits 0      (0x0)
Reg ERROR        4 bits 2      (0x2) Reg COUNTER      8 bits 1      (0x1)
Reg ERROR        4 bits 4      (0x4) Reg COUNTER      8 bits 1      (0x1)
Reg ERROR        4 bits 2      (0x2) Reg COUNTER      8 bits 2      (0x2)
Reg ERROR        4 bits 4      (0x4) Reg COUNTER      8 bits 2      (0x2)
Reg ERROR        4 bits 2      (0x2) Reg COUNTER      8 bits 3      (0x3)
Reg ERROR        4 bits 2      (0x2) Reg COUNTER      8 bits 3      (0x3)
Reg ERROR        4 bits 4      (0x4) Reg COUNTER      8 bits 3      (0x3)
Reg ERROR        4 bits 9      (0x9) Reg COUNTER      8 bits 4      (0x4)
Cycles : 10
--------------------       Ended execution      --------------------
0     0  A0 0C D5
1     3  A0 9D D0
2     6  B0 32 00
3     9  A2 D0 D5
4    12  CF FF FF
5    15  FF FF FF
   [same x250]

Pin V16alpha    32 pins 01001000000000000000000000001100
                        ^^   ^^ ^       ^
```
`ERROR` contains the current status code (`9` is the code for execution ended). `COUNTER` points to the current instruction in the program register, and it stops at `4` because instructions are 3 bytes long. You can see the state of the **program data** containing the machine code at the end of execution, and the state of the **external pins**. To understand more about the status codes, instructions or general workings, I invite you to read [the fabulous manual](v16alpha/v16alpha.md).




### Note on methodology

Proper methodology is not followed here, in that I'm catching exceptions to instead set error codes on small registers that could overflow.. Code is repeated, documentation is synced by hand with the implementation when it could be automated, etc. This is how I have fun `:]`