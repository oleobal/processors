V16α processor (V16alpha)
=========================

The V16alpha is a general-purpose 16 bit processor that lacks all the
features you would wish, and has all sorts of things you wish it didn't.


### Facilities

The following registers are provided :

 - `RINT` (internal), general purpose, used for arithmetic (16 bits)
 - `RINO` (input/output), supposed to be connected to a bus (16 bits)
 
In addition, other registers are used for operation of mostly automatic
components :
 
 - `RERR` (error), set by the processor during operation (8 bits)
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

Running the processor when it is on error code 9 automatically resets
the program counter to 0.

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


### Status codes

Available by checking `RERR`, an 8-bit register. Codes :

| Code | Hex | Status                   |
|------|-----|--------------------------|
| 0    | 0   | Processor ready          |
| 1    | 1   | No program               |
| 2    | 2   | Executing                |
| 3    | 3   | Skipped a 0xFF operator  |
| 4    | 4   | Finished current instr   |
|      |     |                          |
| 9    | 9   | Finished execution       |
|      |     |                          |
| 10   | A   | Invalid operation        |
| 11   | B   | Invalid operand          |
| 12   | C   | Wrong number of operands |
|      |     |                          |
| 255  | FF  | Other                    |






