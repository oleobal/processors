V16α processor (V16alpha)
=========================

The V16alpha is a general-purpose 16 bit processor that lacks all the
features you would wish, and has all sorts of things you wish it didn't.

It most notably has an internal program memory (for up to 256 instructions),
allowing the full use of its 24 I/O pins. (instructions can still be fetched,
of course).


### Facilities

The following registers are provided :

 - `RINT` (internal), general purpose, used for arithmetic (16 bits)
 - `RIOA` (input/output), supposed to be connected to a bus (16 bits)
   `RIOA` is also used for program loading.
 - `RIOB` (input/output), supposed to be connected to a bus (8 bits)
 - `RINO` redirects to RIOA
 
In addition, other registers are used for operation of mostly automatic
components :
 
 - `RERR` (error), set by the processor during operation (4 bits)
 - `RCNT` (counter), pointing to the current instructions (8 bits)
 - `RSTA` (stack), pointing to the current stack level (4 bits)

`RCNT` and `RSTA` work the same way, in that they both address a memory
unit. On the V16alpha, "memory units" are arrays of data that cannot be
used directly by programs. They use specialized operations instead.

`RCNT` addresses instructions, which are 3 bytes long (operator, 
operand 1, operand 2). If the operands are not present, they are
replaced with `0xFF` padding. `RCNT` is thus addressing 768 bytes
(256 instructions). The data unit it addresses is filled with ones
(`0xFF`) at initialization. You may also use `DLPR` to load data from
the unit into a register, and `DSPR` to store data into the unit.
Note that these instructions address the unit byte per byte, unlike
`RCNT` !

The stack addressed by `RSTA` is a memory unit of 256 bits, which is
split in thirty-two 8-bits values. It can be addressed randomly, but
supports stack operations and is referred to as the stack. The data
unit it addresses is filled with zeroes (`0x00`) at initialization.
You can use `POP` and `PUSH` for automatic operation, or `DLST` and
`DSST` for loading/storing into the unit.

### Pinout

<img src="./v16alpha_pinout.svg" width="100%" height="500">

(Alimentation/Ground pins not represented)

| No  | Name    | Description                                 |
|-----|---------|---------------------------------------------|
| 1   |Clock    | Front (1) triggers cycle (proc resets to 0) |
|2-5  |Error    | Exposes the status code (read only)         |
|6    |Prog load| Order the loading of an instruction         |
|7-8  |P offset | Control where a loaded instruction is set   |
|9-16 | I/O B   | Read/write the proc's I/O B register        |
|17-32| I/O A   | R/W the proc's I/O A register, load programs|

Important : Pins are numbered 1-32 here, but they might be 0-indexed in some
applications, so remember to check.

```
// pinset description
# title
V16alpha
# top ; mark
# end

< Clock
# red
4x > Error
# end
1x < Prog load
2x < P offset
# blue
8x <> I/O_B
# green
16x <> I/O_A
```


### Assembly

Assembly for the V16alpha is a list of commands of the form :

`<OP> [target or value] [target or value]`

Values are in decimal or hexadecimal (prefixed with `0x`), from 0
to 159. Targets are generally data units such as registers.

Lines starting with `#` are comments, and not parsed.

Operations :

|  OP   | operand 1 | operand 2 | Description                 | Cost |
|-------|-----------|-----------|-----------------------------|------|
| STORE | value/reg | reg       | Store op1 in op2            | 2    |
| DLPR  | value/reg | reg       | Load program[op1] to op2    | 3    |
| DSPR  | value/reg | value/reg | Store op1 to program[op2]   | 3    |
| DLST  | value/reg | reg       | Load stack[op1] to op2      | 3    |
| DSST  | value/reg | value/reg | Store op1 to stack[op2]     | 3    |
| PUSH  | value/reg |           | Push a value onto the stack | 2    |
| POP   | reg       |           | Pop the topmost value       | 2    |
|       |           |           |                             |      |
| ADD   | value/reg | reg       | Add op1 to op2 in op2       | 2    |
|       |           |           |                             |      |
| END   |           |           | End execution               | 1    |

Costs in number of cycles. When a register is specified instead of a
literal value, its value is used.

Operation ends either on fatal error (check `RERR`), on `END`
instruction, or when reaching the end of the program table
(both produce error code `9`).

Running the processor when it is on error code `9` automatically resets
the program counter to `0`.

### Machine code

Operators and operands are one byte each. Each instruction is three
bytes long, with `0xFF` used to pad instructions that have less than
two operands.

Operands up to `0x9F` are taken as values, as is.
(values above 159 thus cannot be represented directly in machine code,
and have to be computed)
Values from `0xA0` are reserved for keywords, up to `0xCF`.
Values from `0xD0` are reserved for data, up to `0xFE`.

Machine code/operator table :

|  OP   | Code |
|-------|------|
| STORE |`0xA0`|
| DLPR  |`0xA1`|
| DSPR  |`0xA2`|
| DLST  |`0xA3`|
| DSST  |`0xA4`|
| PUSH  |`0xA5`|
| POP   |`0xA6`|
|       |      |
| ADD   |`0xB0`|
|       |      |
| END   |`0xCF`|

In addition, `0xFF` serves as a 'skip this instruction' operator.

Codes for registers :

| Register | Code |
|----------|------|
| RINT     |`0xD0`|
| RERR     |`0xD1`|
| RINO     |`0xD2`|
| RCNT     |`0xD3`|
| RSTA     |`0xD4`|
| RIOA     |`0xD5`|
| RIOB     |`0xD6`|

### Loading a program

The V16alpha uses the I/O A register for loading instruction.

Remember that machine code instructions are three bytes long. The processor can
hold 256 three-bytes instructions.

To load an instruction :
 1. Set the first 8 pins of the I/O A bus to the index to put the instr at
 2. Set the last 8 pins of the same bus to the byte to write
 3. Set the `Prog ctrl` pins to what the byte is :
     1. (`00`) instruction
     2. (`01`) first operand
     3. (`10`) second operand 
 4. Set the `Prog load` pin to `1`

The processor checks these pins each time it finishes an instruction (code `4`).
The loading takes three cycles. The error code is set to `5` for the first cycle
of the loading, after which it is set to `2` (like for any instruction).

The `Prog load` and `Prog ctrl` pins are all set to `0` after reading.

### Running and resetting

Cycling the processor when `Prog load` is at `0` will execute instructions.

Cycling when the error code is `9` (finished execution) will automatically
reset the program counter to 0 before continuing execution.

Setting the `Prog load` and both `Prog ctrl` pins to 1 (checked when an
instruction is finished) will reset the program counter and the error code
to `0`. No further development happens that cycle.

Once the fifth consecutive cycle in that state is reached, the processor is
entirely reset (cycle count, pins, registers, stack, and program memory),
a process taking 1 cycle.

The `Prog load` and `Prog ctrl` pins are all set to `0` after reading. Do set
them back up to `1` for resetting.

### Status codes

Available by checking `RERR`, a 4-bit register. Codes :

| Code | Hex | Status                   |
|------|-----|--------------------------|
| 0    | 0   | Processor ready          |
| 1    | 1   | No program               |
| 2    | 2   | Executing                |
| 3    | 3   | Skipped a 0xFF operator  |
| 4    | 4   | Finished current instr   |
| 5    | 5   | Started loading instr    |
| 9    | 9   | Finished execution       |
|      |     |                          |
| 10   | A   | Invalid operation        |
| 11   | B   | Invalid operand          |
| 12   | C   | Wrong number of operands |
|      |     |                          |
| 15   | F   | Other                    |