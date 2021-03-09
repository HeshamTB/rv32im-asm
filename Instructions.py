
class Instruction:
    """
    Instruction class: takes several inputs based on the format of the instruction. Then function to_binary returns
    the binary representation.
    """
    # Init
    def __init__(self, instr, frmt='R', imm='0', func7='0', rs2='0', rs1='0', func3='0', rd='0'):
        self.instr = instr
        self.imm = imm
        self.func7 = func7
        self.rs2 = rs2
        self.rs1 = rs1
        self.func3 = func3
        self.rd = rd
        self.frmt = frmt.capitalize()

    # return binary representation
    def to_binary(self):
        """
        A function that organize converts the passed arguments into a binary representation and returns it to caller.
        :return: binary representation of a line of instructions
        """

        # Note: The notation    SomeList[::-1]      just inverts the list
        # we use this feature to be able to deal with lists like a hardware description language
        # without using myHDL library

        if self.frmt == 'R':
            opcode = '0110011'
            return self.func7 + self.rs2 + self.rs1 + self.func3 + self.rd + opcode

        elif self.frmt == 'I':
            if self.instr[0] == 'l':  # A load instruction
                opcode = '0000011'
            elif self.instr == 'jalr':
                opcode = '1100111'
            elif self.instr == 'ecall':
                return '00000000000000000000000001110011'
            elif self.instr == 'ebreak':
                return '00000000000100000000000001110011'
            else:  # normal immediate instruction
                opcode = '0010011'

            if self.instr == 'slli' or self.instr == 'srli':
                self.imm = self.imm[::-1]
                self.imm = '0000000' + self.imm[4::-1]
            elif self.instr == 'srai':
                self.imm = self.imm[::-1]
                self.imm = '0100000' + self.imm[4::-1]
            return self.imm + self.rs1 + self.func3 + self.rd + opcode

        elif self.frmt == 'S':
            opcode = '0100011'
            temp = self.imm[::-1]
            lower_imm = temp[4::-1]
            upper_imm = temp[11:4:-1]  # from bit 11 to bit 5 (4 is not included)
            return upper_imm + self.rs2 + self.rs1 + self.func3 + lower_imm + opcode

        elif self.frmt == 'B':
            opcode = '1100011'
            # only bits 12:1 excluding bit 0, which is always equal to 0
            temp = self.imm[::-1]
            imm_11 = temp[11]
            imm_4 = temp[4:0:-1]  # from bit 4 to bit 1 (0 is not included)
            imm_10 = temp[10:4:-1]  # from bit 10 to bit 5 (4 is not included)
            imm_12 = temp[12]
            return imm_12 + imm_10 + self.rs2 + self.rs1 + self.func3 + imm_4 + imm_11 + opcode

        elif self.frmt == 'U':
            if self.instr == "lui":
                opcode = '0110111'
            else:
                opcode = '0010111'
            return self.imm + self.rd + opcode

        elif self.frmt == 'J':
            opcode = '1101111'
            temp = self.imm[::-1]
            imm_20 = temp[20]
            imm_19 = temp[19:11:-1]
            imm_11 = temp[11]
            imm_10 = temp[10:0:-1]  # 0 is not included
            return imm_20 + imm_10 + imm_11 + imm_19 + self.rd + opcode


# ----------------------------- Main Dictionary ----------------------- #
# This nested dictionary contains all the instructions and their types, and other fixed information
all_instructions = {'R': [{'inst': 'add', 'func3': '000',  'func7': '0000000'},
                          {'inst': 'sub', 'func3': '000',  'func7': '0100000'},
                          {'inst': 'xor', 'func3': '100',  'func7': '0000000'},
                          {'inst': 'or',  'func3': '110',  'func7': '0000000'},
                          {'inst': 'and', 'func3': '111',  'func7': '0000000'},
                          {'inst': 'sll', 'func3': '001',  'func7': '0000000'},
                          {'inst': 'srl', 'func3': '101',  'func7': '0000000'},
                          {'inst': 'sra', 'func3': '101',  'func7': '0100000'},
                          {'inst': 'slt', 'func3': '010',  'func7': '0000000'},
                          {'inst': 'sltu', 'func3': '011', 'func7': '0000000'}],

                    # The I needs to fix dividing the imm.
                    'I': [{'inst': 'addi',  'func3':  '000'},
                          {'inst': 'xori',  'func3':  '100'},
                          {'inst': 'ori',   'func3':  '110'},
                          {'inst': 'andi',  'func3':  '111'},
                          {'inst': 'slli',  'func3':  '001'},
                          {'inst': 'srli',  'func3':  '101'},
                          {'inst': 'srai',  'func3':  '101'},
                          {'inst': 'slti',  'func3':  '010'},
                          {'inst': 'sltiu', 'func3':  '011'},
                          {'inst': 'lb',    'func3':  '000'},
                          {'inst': 'ln',    'func3':  '001'},
                          {'inst': 'lw',    'func3':  '010'},
                          {'inst': 'lbu',   'func3':  '100'},
                          {'inst': 'lhu',   'func3':  '101'},
                          {'inst': 'jalr',  'func3':  '000'},
                          {'inst': 'ecall', 'func3':  '000'},
                          {'inst': 'ebreak', 'func3': '000'}],

                    'S': [{'inst': 'sb', 'func3': '000'},
                          {'inst': 'sh', 'func3': '001'},
                          {'inst': 'sw', 'func3': '010'}],

                    'B': [{'inst': 'beq', 'func3':  '000'},
                          {'inst': 'bne', 'func3':  '001'},
                          {'inst': 'blt', 'func3':  '100'},
                          {'inst': 'bge', 'func3':  '101'},
                          {'inst': 'bltu', 'func3': '110'},
                          {'inst': 'bgeu', 'func3': '111'}],

                    'U': [{'inst': 'lui'}, {'inst': 'auipc'}],

                    'J': [{'inst': 'jal'}]}

# ----------------------- Testing Area ------------------------ #

if __name__ == '__main__':
    test = ''
    for key, value in all_instructions.items():  # loop over all types
        for v in value:  # loop over all instructions inside a certain type
            if v['inst'] == test:  # if the value corresponding to the key 'inst' is identical to the input:
                if key == 'R':
                    print(Instruction(instr=v['inst'], frmt=key, func7=v['func7'], rs2='00010',
                                      rs1='00001', func3=v['func3'],
                                      rd='00000').to_binary())
                elif key == 'I':
                    print(Instruction(instr=v['inst'], frmt=key, imm='00000000001', rs1='00001',
                                      func3=v['func3'], rd='00000').to_binary())
                elif key == 'S':
                    print(Instruction(instr=v['inst'], frmt=key, imm='00000000001', rs2='10000',
                                      rs1='00001', func3=v['func3'],
                                      rd='00000').to_binary())
                elif key == 'B':
                    print(Instruction(instr=v['inst'], frmt=key, imm='00000000001', rs2='10000',
                                      rs1='00001', func3=v['func3'],
                                      rd='00000').to_binary())
                elif key == 'U':
                    print(Instruction(instr=v['inst'], frmt=key, imm='00000000001', rd='00000').to_binary())
                elif key == 'J':
                    print(Instruction(instr=v['inst'], frmt=key, imm='00000000001', rd='00000').to_binary())
