### Fantasy processor(s)

This repository is meant to be a collection of emulated components. I'm only looking to emulate a vague abstraction of the interface, not the actual electrical workings.

The only one as of now is the V16alpha, a 16-bits processor. Files :

 - `v16alpha/v16alpha.md` contains [the manual](v16alpha/v16alpha.md)
 - `v16alpha/v16alpha.py` contains the actual processor as a class
 - `v16alpha/v16alpha_asm.py` contains the assembler
 - `v16alpha_test.py` can be executed to test the processor

It is still lacking many instructions and [the pinout](v16alpha/v16alpha_pinout.svg) is still only on paper. Still, I have an interesting example.

The assembly code :
```
STORE 21 RINT
# cannot write 0xCF, have to compute it
PUSH 157
POP RINO
ADD 50 RINO
DSPR RINO RINT
```

Seeks to place `0xCF`, the end instruction, into the program memory of the processor to end execution. It cannot do so, because V16alpha machine code uses byte words where everything above `0x9F` is reserved, and everything beneath is a numeric literal. So it stores 157 into the I/O register (used as general purpose here), and adds 50 to it to compute the end instruction, before writing it at index 21 in the program memory.

Execution :
```
Reg ERROR        5 bits val 0      (0x0)
Reg INTERNAL    16 bits val 0      (0x0)
======     Starting execution     ======
Reg ERROR        5 bits val 2      (0x2) Reg COUNTER      8 bits val 0      (0x0)
Reg ERROR        5 bits val 4      (0x4) Reg COUNTER      8 bits val 0      (0x0)
Reg ERROR        5 bits val 2      (0x2) Reg COUNTER      8 bits val 1      (0x1)
Reg ERROR        5 bits val 4      (0x4) Reg COUNTER      8 bits val 1      (0x1)
Reg ERROR        5 bits val 2      (0x2) Reg COUNTER      8 bits val 2      (0x2)
 [... this repeats...]
Reg ERROR        5 bits val 3      (0x3) Reg COUNTER      8 bits val 6      (0x6)
Reg ERROR        5 bits val 3      (0x3) Reg COUNTER      8 bits val 7      (0x7)
Reg ERROR        5 bits val 9      (0x9) Reg COUNTER      8 bits val 7      (0x7)
======       Ended execution      ======
Program data :
   0 A0 15 D0
   3 A5 9D FF
   6 A6 D2 FF
   9 B0 32 D2
  12 A2 D2 D0
  15 FF FF FF
   [same]
  21 CF FF FF
  24 FF FF FF
   [same x247]

Reg INTERNAL    16 bits val 21     (0x15)
Reg IO          16 bits val 207    (0xCF)
Cycles : 16
```
ERROR contains the current status code (`9` is the code for execution ended). `COUNTER` points to the current instruction in the program register, and it stops at 7 because instructions are 3 bytes long. You can see the state of the program data containing the machine code at the end of execution. To understand more about the status codes, instructions or general workings, I invite you to read [the fabulous manual](v16alpha/v16alpha.md).




### Note on methodology

Proper methodology is not followed here, in that I'm catching exceptions to instead set error codes on small registers that could overflow.. Code is repeated, documentation is synced by hand with the implementation when it could be automated, etc. This is part of the game.