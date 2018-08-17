V16α processor (V16alpha)
=========================

The V16alpha is a general-purpose 16 bit processor that lacks all the
features you would wish, and has all sorts of things you wish it hadn't.


### Facilities

The following registers are provided :

 - `RINT` (internal), general purpose, used for arithmetic (16 bits)
 - `RINO` (input/output), supposed to be connected to a bus (16 bits)
 
In addition, other registers are used for operation of mostly automatic
components :
 
 - `RERR` (error), set by the processor during operation (8 bits)
 - `RCNT` (counter), pointing to the current instructions (16 bits)
 - `RSTA` (stack), pointing to the current stack level (4 bits)


The stack addressed by `RSTA` is a memory unit of 256 bits, which is
split in thirty-two 8-bits values.

### Operations

Assembly for the V16alpha is a list of commands of the form :

`<OP> <target or value> [target or value]`

Operations :

|  OP   | operand 1 | operand 2 | Description            |
|-------|-----------|-----------|------------------------|
| STORE | value/reg | reg       | Stores oper1 in oper2  |
|       |           |           |                        |

### Machine code

Operators and operands are one byte each.
Operations are delimited by `0xFF`.

Operands up to `0x1F` are taken as values, as is.
(values above 159 thus cannot be represented directly in machine code,
and have to be computed)
Values from `0xA0` are reserved for keywords, up to `0xCF`.
Values from `0xD0` are reserved for data, up to `0xFE`.

Machine code/operator table :

|  OP   | Code |
|-------|------|
| STORE |`0xA0`|
|       |      |

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
| 3    | 3   | Finished execution       |
|      |     |                          |
| 10   | A   | Invalid operation        |
| 11   | B   | Invalid operand          |
| 12   | C   | Wrong number of operands |
|      |     |                          |
| 255  | FF  | Other                    |







