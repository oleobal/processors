V16α processor (V16alpha)
=========================

One 16-bits register `register`. General purpose, used for arithmetic. 

One 16-bits register `io`, supposed to be connected to a bus for I/O.

One 8-bits register `status`, set by the processor during operation.

One unlimited-size `program` (list of string instructions)

One 16-bits register `programCounter`, addressing string instructions.



### Status codes

Available by checking `status`, an 8-bit register. Codes :

| Code | Hex | Status             |
|------|-----|--------------------|
| 0    | 0   | Processor ready    |
| 1    | 1   | No program         |
| 2    | 2   | Finished execution |
|      |     |                    |
| 255  | FF  | Other              |







