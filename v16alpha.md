V16α processor (V16alpha)
=========================

The V16alpha is an amazing processor that manages to work DIRECTLY from
assembly code! This does put some restrictions on the user, but we are
confident our clients are competent enough.


### Facilities

The following registers are provided :

 - One 16-bits register `RINT`, general purpose, used for arithmetic
 - One 16-bits register `RINO`, supposed to be connected to a bus
 
In addition, other registers are used for operation of mostly automatic
components :
 
 - One 8-bits  register `RERR`, set by the processor during operation
 - One 16-bits register `RCNT`, pointing to the current instructions
 - One 4-bits register `RSTA`, pointing to the current stack level

Because the V16alpha program memory contains assembly and not machine
code, it is not possible to retrieve values from it.

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







