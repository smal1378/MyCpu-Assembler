# this is file is the core of assembler,
from typing import Iterable, Union
from Queue import Queue

ver = "1.1"


class AssembleSyntaxError(TypeError):
    pass


class Assembler:
    class QNode:
        """
        This class is used in queue for JP command, each node
        can be waiting for its JP to be found or be ready to
        get yielded out.
        """

        def __init__(self, code: str, line_num: Union[None, int],
                     jp_name: Union[str, None]):
            self.code = code
            self.line_num = line_num
            self.jp_name = jp_name

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

    def __init__(self, reader_handler: Iterable[str]):
        """

        :param reader_handler: an iterable containing strings of each line
        of file
        """
        self.reader_handler = reader_handler
        self.jump_points = {}  # jump_point_name: 3bits_addr
        self.variables = {}  # variable name: (address, init_value) of it
        self.variable_names = []  # ordered variable names for yielding
        # them in order to the output.
        self.last_free_addr = 0x1  # used for variables
        self.current_addr = None  # used for instructions
        self.queue = Queue()  # used make JP work, contains QNode

    def __check_variable(self, line_num, ins):
        if ins[0].lower().strip() == "var":
            # Defining variable
            if (len(ins) != 3 or ins[1] in self.variables or
                    ins[1].lower() in self.instructions or
                    ins[1][0].isnumeric() or self.current_addr is not None):
                raise AssembleSyntaxError(f"Invalid syntax or variable name"
                                          f" at {line_num}")
            # following line will add the address and init value of the var
            self.variables[ins[1]] = (
                self.last_free_addr, self.__get_hex(ins[2], line_num))
            self.variable_names.append(ins[1])
            self.last_free_addr += 1
            return True
        return False

    @staticmethod
    def __remove_comment(line: str):
        index = line.find("#")
        if index >= 0:
            return line[:index]
        return line

    def __check_jp(self, line_num, ins):
        if len(ins) > 0 and ins[0].lower() == "jp":
            if (len(ins) == 2 and ins[1] not in self.jump_points and
                    ins[1] not in self.variables and ins[1][0].isalpha() and
                    ins[1].lower() not in self.instructions):
                self.jump_points[ins[1]] = self.current_addr
                return True
            else:
                raise AssembleSyntaxError(f"Invalid JP syntax or Invalid JP "
                                          f"name at line {line_num}")
        return False

    def __check_group1_ins(self, line_num, ins):
        """
        check for load, store, add, and
        """
        if len(ins) >= 1 and ins[0].lower() in ("add", "load", "and", "store"):
            if len(ins) == 2:
                self.current_addr += 1
                ins_code, ins_addr = self.instructions[ins[0].lower()]
                tmp = hex(ins_code)[2:]  # instruction address in hex
                tmp2 = self.__get_hex(ins[1], line_num)
                ins.clear()  # for letting caller know that it worked
                yield tmp + tmp2[1:]
            else:
                raise AssembleSyntaxError(f"Invalid Syntax at line {line_num}"
                                          f" - Instruction must be two parts")

    def __check_group2_ins(self, line_num, ins):
        if len(ins) >= 1 and ins[0].lower() in ("comp", "lsl"):
            if not len(ins) == 1:
                raise AssembleSyntaxError(f"Invalid Syntax, Instruction must"
                                          f"one part - at line {line_num}")
            ins_code, tmp = self.instructions[ins[0].lower()]
            self.current_addr += 1
            ins.clear()
            yield self.__get_hex(ins_code, line_num)[0] + "000"

    def __check_group3_ins(self, line_num, ins):
        if len(ins) >= 1 and ins[0].lower() in ("jump", "jumpz"):
            if len(ins) == 2:
                ins_code, tmp = self.instructions[ins[0]]
                if ins[1] in self.jump_points:
                    tmp = hex(ins_code)[2:]  # instruction address in hex
                    tmp2 = self.__get_hex(self.jump_points[ins[1]], line_num)
                    yield tmp + tmp2[1:]
                else:
                    tmp = hex(ins_code)[2:] + "000"
                    self.queue.put(Assembler.QNode(tmp, line_num, ins[1]))
                self.current_addr += 1
                ins.clear()
            else:
                raise AssembleSyntaxError(f"Invalid Syntax, jump needs a JP at"
                                          f" line {line_num}")

    def __mainloop(self):
        # read every line from the input
        for line_num, line in enumerate(self.reader_handler):
            # comments
            line = self.__remove_comment(line)
            if not line:
                continue

            ins = line.split()

            # variables
            if self.__check_variable(line_num, ins):
                continue

            # check if first ins after VAR definitions and insert them
            if self.current_addr is None:
                # means this is last VAR define, so lets begin instruction part
                self.current_addr = self.last_free_addr
                # now lets first insert the lines into the file
                # first of all we have to tell it to jump to the last free
                # place available after all variables
                tmp = hex(self.current_addr)[2:]
                yield "4" + ("0" * (3 - len(tmp))) + tmp
                # now we have to insert variables
                # it's already ordered, so starts from 1
                for var_name in self.variable_names:
                    yield self.variables[var_name][1]

            # jump points
            if self.__check_jp(line_num, ins):
                continue

            if not ins[0].lower() in self.instructions:
                raise AssembleSyntaxError(f"Invalid instruction name "
                                          f"at line {line_num}")

            # check - load, store, add, and,
            yield from self.__check_group1_ins(line_num, ins)
            if not ins:
                continue

            # check - comp, lsl,
            yield from self.__check_group2_ins(line_num, ins)
            if not ins:
                continue

            # check - jump, jumpz
            yield from self.__check_group3_ins(line_num, ins)
            if not ins:
                continue

            raise AssembleSyntaxError(f"Unknown syntax at line {line_num}")

        # the for has ended, lets check if current_addr is None
        if self.current_addr is None:
            self.current_addr = self.last_free_addr
            # first of all we have to tell it to jump to the last free place
            # available after all variables
            tmp = hex(self.current_addr)[2:]
            yield "4" + ("0" * (3 - len(tmp))) + tmp
            # now we have to insert variables
            # it's already ordered, so starts from 1
            for var_name in self.variable_names:
                yield self.variables[var_name][1]
        # now let's add a loop at the end of code.
        tmp = hex(self.current_addr)[2:]
        yield "4" + ("0" * (3 - len(tmp))) + tmp

    def __get_hex(self, _input: Union[int, str], line_num: int) -> str:
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
            if _input.isnumeric():
                num = hex(int(_input))[2:]
                return ("0" * (4 - len(num))) + num
            elif len(_input) > 2 and "x" == _input[1].lower() and \
                    _input[0] == "0" and self.__ishex(_input[2:]):
                num = hex(int(_input, 16))[2:]
                return ("0" * (4 - len(num))) + num
            elif _input in self.variables:
                num = hex(self.variables[_input][0])[2:]
                return ("0" * (4 - len(num))) + num
            else:
                raise AssembleSyntaxError("Invalid syntax while converting to "
                                          f"hex at line {line_num}")
        else:
            raise AssembleSyntaxError("Invalid func argument")

    @staticmethod
    def __ishex(_input: str) -> bool:
        """
        checks whether all characters in _input is 0 to 9 and a to f
        """

        return all(map(Assembler.__ishex_tool1, _input))

    @staticmethod
    def __ishex_tool1(ch):
        return ch.isnumeric or ch.lower() in "abcdef"

    def run_assemble(self):
        for i in self.__mainloop():
            if self.queue.empty():
                yield i
            else:
                self.queue.put(Assembler.QNode(i, None, None))
                waiting_code: Assembler.QNode = self.queue.show()
                if waiting_code.jp_name in self.jump_points:
                    while not self.queue.empty():
                        item: Assembler.QNode = self.queue.show()
                        if item.jp_name is None:
                            self.queue.get()
                            yield item.code
                        elif item.jp_name in self.jump_points:
                            self.queue.get()
                            addr = self.__get_hex(self.jump_points
                                                  [item.jp_name],
                                                  item.line_num)[1:]
                            yield item.code[0] + addr
                        else:
                            break


if __name__ == '__main__':
    x = [
        "VAR hello 500",
        "jump loop",
        "jump hi",
        "load hello",
        "add hello",
        "store hello",
        "JP loop",
        "load 0x1",
        "JP hi",
        "load 0x2"
    ]
    a = Assembler(x)
    for i in a.run_assemble():
        print(i, end=" - ")