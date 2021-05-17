# MyCpu-Assembler
This is an assembler written in Python for von neumann cpu architecture which I 
implemented using 'logisim2.7.1'.


CPU is a 16bits type and first 4bits are opcode, other 12 bits are address.
as there is only one single register which is called Accumulator (AC for short)
so all operations will be done on this and no register name is given in 
statements.

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

- other commands of this cpu will be added later when added to cpu design in 
  "logisim2.7.1".

# Syntax

1. Variables must be defined at first lines, then the code. no indentation must
   be applied.
2. Variables names shouldn't be repetitive, or an instruction name, they can't 
   start with numbers. all other characters are supported.
3. Variable definition: "VAR var_name binary_initial_value".
4. Variables are case-sensitive, but not the instructions.
5. Comments are lines that start with '#'. exp: "# your comment"
   new in ver 1.1: comments can be any text after "#". (in line comments)
6. Blank lines are ignored.
7. Non-Addressed Instructions like COMP and LSL does not support address field.
   exp: "COMP"
8. Address is var_name like "my_var", hex like "0x5f" or int like "57".
9. Addressed Instructions like Add or Store accept one address. exp: 
   "ADD my_var"
10. JUMP and JUMPX gets jump_points, variables or direct addresses, it's 
    recommended to use jump_points due to safety.
11. jump_points are defined in separate lines and before where you want to 
    jump, defined with JP keyword. exp: "JP hello_there".
    jump_point name must be unique between variables and other jump_points.

## future syntax
12. Indirect addressing are a bit complex to be assembled, I'm working 
    on its syntax for now.
