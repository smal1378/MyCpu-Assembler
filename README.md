# MyCpu-Assembler
This is an assembler written in Python for newman cpu.


CPU is a 16bits type and first 4bits are opcode, other 12 bits are address.
as there is only one single register which is called Accomulator (AC for short) so all operations will be done on this and no register name is given in statements.

# ISA
1. LOAD -> 0x0
2. ILOAD -> 0x8
3. STORE -> 0x1
4. ISTORE -> 0x9
5. ADD -> 0x2
6. IADD -> 0xA
7. AND -> 0x3
8. IAND -> 0xB
9. JUMP -> 0x4
10. IJUMP -> 0xC
11. JUMPZ -> 0x5
12. IJUMPZ -> 0xD
13. COMP -> 0x6
14. LSL -> 0x7

- other commands of this cpu will be added later as added to cpu design in
