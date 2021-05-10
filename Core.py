# this is file is the core of assembler,
from typing import Iterable, Union
ver = "1.0"


class AssembleSyntaxError(TypeError):
    pass


def assemble(reader_handler: Iterable[str]) -> Iterable[bytes]:
    """
    Will assemble the lines of code in reader_handler
    :param reader_handler: an iterable containing strings of each line
    of file
    """

    # noinspection SpellCheckingInspection
    instructions = {
        # ins: (hex_code, accepts_addr)
        "load": (0x0, True),
        "iload": (0x8, True),
        "store": (0x1, True),
        "istore": (0x9, True),
        "add": (0x2, True),
        "iadd": (0xA, True),
        "and": (0x3, True),
        "iand": (0xB, True),
        "jump": (0x4, True),
        "ijump": (0xC, True),
        "jumpz": (0x5, True),
        "ijumpz": (0xD, True),
        "comp": (0x6, False),
        "lsl": (0x7, False)
    }

    variables = {}  # variable name: (address, init_value) of it
    variable_names = []  # just needed ordered variable names for inserting
    # them in order to the output.
    last_free_addr = 0x1
    current_addr = None

    for line_num, line in enumerate(reader_handler):
        # read every line from the input
        ins = line.split()
        if not ins or ins[0][0] == "#":  # comments or blank lines
            continue
        if ins[0].lower().strip() == "var":
            # Defining variable
            if (len(ins) != 3 or ins[1] in variables or
                    ins[1].lower() in instructions or
                    ins[1][0].isnumeric() or current_addr is not None):
                raise AssembleSyntaxError("Invalid syntax or variable name")
            # following line will add the address and init value of the var
            variables[ins[1]] = (last_free_addr, __get_hex(ins[2], line_num,
                                                           variables))
            variable_names.append(ins[1])
            last_free_addr += 1
            continue
        if not ins[0].lower() in instructions:
            raise AssembleSyntaxError(f"Invalid instruction name "
                                      f"at line {line_num}")
        ins_code, ins_addr = instructions[ins[0].lower()]

        if ins_addr and len(ins) != 2:
            raise AssembleSyntaxError(f"Instruction doesn't accept address -"
                                      f" at line {line_num}")
        if current_addr is None:
            current_addr = last_free_addr
            # now lets first insert the lines into the file
            # first of all we have to tell it to jump to the last free place
            # available after all variables
            tmp = hex(current_addr)[2:]
            yield "4" + ("0" * (3 - len(tmp))) + tmp
            # now we have to insert variables
            # it's already ordered, so starts from 1
            for var_name in variable_names:
                yield variables[var_name][1]

        if not ins_addr and len(ins) == 1:  # those who doesn't have address
            yield __get_hex(ins_code, line_num, variables)
        elif len(ins) == 1:  # non-addressed ins, but got an address
            raise AssembleSyntaxError(f"Invalid Syntax, got address "
                                      f"at line {line_num}")
        elif ins_addr and len(ins) == 2:  # those who has address
            tmp = hex(ins_code)[2:]  # instruction address in hex
            tmp2 = __get_hex(ins[1], line_num, variables)
            yield tmp + tmp2[1:]
        else:
            raise AssembleSyntaxError(f"Invalid Syntax at line {line_num}")
        current_addr += 1
    # the for has ended, lets check if current_addr is None
    if current_addr is None:
        current_addr = last_free_addr
        # first of all we have to tell it to jump to the last free place
        # available after all variables
        tmp = hex(current_addr)[2:]
        yield "4" + ("0" * (3 - len(tmp))) + tmp
        # now we have to insert variables
        # it's already ordered, so starts from 1
        for var_name in variable_names:
            yield variables[var_name][1]
    # now let's add a loop at the end of code.
    tmp = hex(current_addr)[2:]
    yield "4" + ("0" * (3 - len(tmp))) + tmp


def __get_hex(_input: Union[int, str], line_num: int, variables: dict) -> str:
    """
    gets a "0x5" hex like or an integer or variable name
    as input and returns hex string.
    :param _input: hex or integer string
    :param line_num: line number for syntax error raising
    :return: hex string
    """
    if isinstance(_input, int):
        res = hex(_input)[2:]
        return ("0" * (4 - len(res))) + res
    elif isinstance(_input, str):
        if "x" == _input[1].lower() and _input[0] == "0":
            num = hex(int(_input, 16))[2:]
            return ("0" * (4 - len(num))) + num
        elif _input.isnumeric():
            num = hex(int(_input))[2:]
            return ("0" * (4 - len(num))) + num
        elif _input in variables:
            num = hex(variables[_input][0])[2:]
            return ("0" * (4 - len(num))) + num
        else:
            raise AssembleSyntaxError("Invalid syntax while converting to hex "
                                      f"at line {line_num}")
    else:
        raise AssembleSyntaxError("Invalid func argument")


if __name__ == '__main__':
    x = [
        "VAR hello 500",
        "LOAD hello",
        "ADD hello",
        "store hello"
    ]
    print(*assemble(x), sep="\n")
