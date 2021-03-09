#!/usr/bin/python

import argparse, re
from Instructions import Instruction, all_instructions
from myhdl import intbv
import myhdl
from Pseudo_code_converter import Pseudo_Converter, isPseudo, instructionCount


# ============================================================================================= #
# ==================================== Initialize section ===================================== #
# ============================================================================================= #


print("RISC-V RV32IM assembler (Team 2)")
verbose = False

# Following RARS Simulator, initialize some addresses:
text_start_address = 0x00400000
data_start_address = 0x10010000

# initialize registers with their different representations:
# 1- By names:
regs = ['zero', 'ra', 'sp', 'gp', 'tp', 't0', 't1', 't2', 's0', 's1',
        'a0', 'a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 's2', 's3', 's4',
        's5', 's6', 's7', 's8', 's9', ' s10', 's11', 't3', 't4', 't5', 't6', 'pc']
# 2- Starting with x:
regsx = ['x0', 'x1', 'x2', 'x3', 'x4','x5','x6','x7','x8','x9','x10','x11','x12','x13','x14','x15','x16','x17'
         ,'x18','x19','x20','x21','x22','x23','x24','x25','x26','x27','x28','x29','x30','x31','']
# 3- By their number:
regs_bin = dict()
regsx_bin = dict()
for i in range(len(regs)):
    regs_bin[regs[i]] = "{0:05b}".format(i)
    regs_bin[regsx[i]] = "{0:05b}".format(i)


# ============================================================================================= #
# =================================== Start of main program =================================== #
# ============================================================================================= #


def main():
    global verbose
    args = parseArgs()
    err = validArgs(args)
    verbose = args['verbose']
    if err is not None:
        log(err, prefix='ERROR')
        return 2
    in_file_name = args['input files'][0]  # One file
    out_file_name = args['output']
    log("Assembly file: %s" % in_file_name)
    log("Output file: %s" % out_file_name)

    # lists to store lines and output binary string
    in_lines = list()
    out_binary_string = list()

    # Start the first pass:
    with open(in_file_name, 'r') as in_file:
        in_lines = in_file.readlines()

    # delete unwanted characters
    in_lines = stripEscapeChars(in_lines)
    #in_lines = replacePseudo(in_lines)
    # calculate the address of each label + write the data output
    labels = calculateLabels(in_lines)
    log(labels)

    # replace every label with it's address
    in_lines = replaceLabels(labels, in_lines)
    in_lines = replacePseudo(in_lines)
    print(in_lines)

    # start second pass:
    address = text_start_address
    for i in range(len(in_lines)):
        in_lines[i] = in_lines[i].strip()
        if not in_lines[i].split() or isLabel(in_lines[i]):
            log('Skipped line %s PC %s' % (in_lines[i], address))
            continue
        # in_words.append(in_lines[i].split())
        # not efficient, refactor
        for inst_type, instructions in all_instructions.items():
            for instruction in instructions:
                word = in_lines[i].split()[0]
                if word == instruction['inst']:
                    args = listInstrArgs(in_lines[i])
                    # if not args: continue
                    inst = instruction['inst']
                    if inst_type == 'R':
                        rd = getRegBin(args[0])
                        rs1 = getRegBin(args[1])
                        rs2 = getRegBin(args[2])
                        log('PC: %s, inst: %s, rd: %s, rs1: %s, rs2: %s' % (address, inst, rd, rs1, rs2))
                        out_binary_string.append(
                            Instruction(instr=inst,
                                        frmt=inst_type,
                                        rd=getRegBin(args[0]),
                                        rs1=getRegBin(args[1]),
                                        rs2=getRegBin(args[2]),
                                        func3=instruction['func3'],
                                        func7=instruction['func7']))
                    elif inst_type == 'I':
                        if not args:  # ecall, ebreak ...
                            log('%s @ %s' % (inst, address))
                            out_binary_string.append(Instruction(instr=inst, frmt=inst_type))
                        else:
                            args_s = parseSTypeArgs(args[1])
                            rd = getRegBin(args[0])
                            if len(args_s) == 0:  # addi t1, 5
                                rs1 = getRegBin(args[1])
                                imm = formatImm(args[2])
                            else:  # lw t1, -8(a0)
                                rs1 = getRegBin(args_s[0])
                                imm = formatImm(args_s[1])
                            imm = intbv(imm)[12:]
                            imm_delta_bin = int(intbv(int(imm))[12:])
                            imm = "{0:012b}".format(imm_delta_bin)
                            log('PC: %s, inst: %s, rd: %s, rs1: %s, imm: %s' % (address, inst, rd, rs1, imm))
                            out_binary_string.append(
                                Instruction(instr=inst,
                                            frmt=inst_type,
                                            rd=rd,
                                            rs1=rs1,
                                            imm=imm,
                                            func3=instruction['func3']))
                    elif inst_type == 'S':
                        log('%s Type args %s' % (inst_type, args))
                        args_s = parseSTypeArgs(args[1])
                        rs2 = getRegBin(args[0])
                        rs1 = getRegBin(args_s[0])
                        imm = formatImm(args_s[1])
                        imm = int(intbv(int(imm))[12:])
                        imm = "{0:012b}".format(imm)
                        log('PC: %s, inst: %s, rs1: %s, rs2: %s, imm: %s' % (address, inst, rs1, rs2, imm))
                        out_binary_string.append(Instruction(
                            instr=inst,
                            frmt=inst_type,
                            imm=imm,
                            func3=instruction['func3'],
                            rs1=rs1,
                            rs2=rs2
                        ))
                    elif inst_type == 'B':  # Reg, Reg, Address
                        rs1 = getRegBin(args[0])
                        rs2 = getRegBin(args[1])
                        imm = formatImm(args[2])
                        imm_delta = imm - address
                        imm_delta_bin = int(intbv(int(imm_delta))[13:])
                        imm = "{0:013b}".format(imm_delta_bin)
                        log('PC: %s, inst: %s, rs1: %s, rs2: %s, imm: %s, delta: %s' % (
                            address, inst, rs1, rs2, imm, imm_delta))
                        out_binary_string.append(
                            Instruction(instr=inst,
                                        frmt=inst_type,
                                        rs1=rs1,
                                        rs2=rs2,
                                        imm=imm,
                                        func3=instruction['func3']))
                    elif inst_type == 'U':  # Reg, Imm
                        rd = getRegBin(args[0])
                        imm = formatImm(args[1])
                        #imm = imm - address
                        imm = int(intbv(imm)[20:])
                        imm = "{0:020b}".format(imm)
                        log('PC: %s, inst: %s, rd: %s, imm: %s' % (address, inst, rd, imm))
                        out_binary_string.append(Instruction(
                            instr=inst,
                            frmt=inst_type,
                            rd=rd,
                            imm=imm
                        ))
                    elif inst_type == 'J':
                        #  This assumes a reg is provided (jal ra, label_add)
                        rd = getRegBin(args[0])
                        imm = formatImm(args[1])
                        imm = imm - address
                        imm = int(intbv(imm)[21:])
                        imm = "{0:021b}".format(imm)
                        log('PC: %s, inst: %s, rd: %s, imm: %s' % (address, inst, rd, imm))
                        out_binary_string.append(Instruction(
                            instr=inst,
                            frmt=inst_type,
                            rd=rd,
                            imm=imm
                        ))
                    else:
                        log('skipped line')
                        continue
                    address += 4

    if verbose:
        for entry in out_binary_string:
            print(entry.to_binary())
    if out_file_name.endswith('.txt'):
        writeOutText(out_file_name, out_binary_string)
    elif out_file_name.endswith('.bin'):
        writeOutBinary(out_file_name, out_binary_string)
# end of main program

# ============================================================================================= #
# ================================= Helping Functions section ================================= #
# ============================================================================================= #


# Initialize some variables needed by the next function
#   1- a dictionary for data types:
data_types = {'.byte': 1, '.half': 2, '.word': 4, '.dword': 8, '.space': '', '.ascii': 1}

#   2- opening two files to write output:
f_bin = open('Data-Binary.bin', 'wb')
f_text = open('Data-Binary-text.txt', 'w')



def calculateLabels(lines : list[str]) -> dict:
    """
     Calculate address for each label in lines
     :returns dict with 'label:' : address
     This assumes all instructions are real RISC-V 32-bit instructions.
     Thus, adding 4 between each instruction.

     Also, writes out (.bin) and (.txt) files representing data section.
    """
    # address variable serves as program counter
    address = 0
    section = 'text'  # default section

    # patterns to recognize a label / directive when we read one
    label_pattern = re.compile('[a-zA-Z0-9]+:')
    directive_pattern = re.compile('.+[a-zA-Z]')  # make this ignore what comes after the first space

    # store labels and their addresses
    label_mapping = dict()

    # Determine whether this is text or data segment
    for i in range(len(lines)):
        if lines[i] == '.data':
            address = data_start_address
            section = 'data'
        elif lines[i] == '.text':
            address = text_start_address
            section = 'text'

        # ---------------------------------- Text Section ---------------------------------- #
        # Rules for text segment:
        #   1- Labels must be alone in the line

        if section == 'text':
            poten_label = label_pattern.match(lines[i])  # a potential label
            debug('labeling line: %s' % lines[i])
            # if the potential label matches the pattern of labels:
            if poten_label:
                debug('Label %s @ %s' %(poten_label.group(), address))
                label = poten_label.group().replace(':', '')
                # Add label with address + 4 since nothing should be after the label, We hope.
                if address == text_start_address:  # or address == 0:
                    label_mapping[label] = address  # First line is different
                else:
                    label_mapping[label] = address
            elif isPseudo(lines[i].split()[0]):
                count = instructionCount(lines[i].split()[0])
                debug('Pseudo with %s insts. PC %s, PC+ %s. %s' % (count, address, address+(count*4), lines[i]))
                address += 4*count
                if count == 0: warn('Could not resolve Pseudo inst: %s' % lines[i].split()[0])
            # Not a label:
            elif isInstr(lines[i]):
                address += 4

        # ---------------------------------- Data Section ---------------------------------- #

        # the rules for data segment:
        #   1- format is [label: .data_type data]
        #   2- if data consist of numbers, is should be separated by commas
        #   3- in case of commas, there must be a space after it
        #   4- if data consist of string, it must be contained in " "
        #   5- all of the above must be in one line
        #   6- text must be declared last, after all numeric data

        # Data Section:
        elif section == 'data':
            poten_label = label_pattern.match(lines[i])  # a potential data label
            # if the potential label matches the pattern of labels:
            if (poten_label):
                data_label = poten_label.group().replace(':', '').strip()
                mod_line = lines[i].replace(data_label + ':', '').strip()  # modify the line, delete the label from it
                poten_dir = directive_pattern.match(mod_line)  # a potential directive
                # if no directive comes after the label, exit, since this is an error (no data type).
                if not poten_dir:
                    print("Error")
                    exit(0)
                # the 'split' in next line will get rid of whatever after the first word
                data_type = poten_dir.group().split(' ', 1)[0]
                mod_line = mod_line.replace(data_type, '').strip()
                # initially, the new address is the current address,
                # then, it will be incremented for the data that comes after it.
                new_address = address
                if data_type == '.ascii':
                    mod_line = mod_line.strip("'").strip('"')
                    new_address = address + data_types['.ascii'] * len(mod_line)
                elif data_type == '.space':
                    new_address = address + int(mod_line)
                elif data_type in data_types:
                    mod_line = mod_line.split(',')
                    new_address = address + data_types[data_type] * len(mod_line)
                else:
                    print("the data type: '" + data_type + "' is not recognized, please make sure it follows the rules"
                                                           "and try again.")
                    exit(0)

                # set the current address to equal the new address, and add the label-address to the dictionary
                label_mapping[data_label] = address
                address = new_address

                # write the output of data segment in (.bin) file:
                data_to_bin(mod_line, data_type)

    log('Located and mapped labels %s' % label_mapping)

    # close file (.bin)
    f_bin.close()
    # write the binary data as text:
    writeOutDataText()
    # close the .txt file
    f_text.close()
    # return the labels and their addresses
    return label_mapping


def data_to_bin(line, data_type):
    """
    A function that takes a line containing data, and slice it into a list of 4 bytes (a word) then write down
    each word into the data output .bin file
    :param line: Line containing data that needs to be stored in memory
    :param data_type: type of the data
    :return: None
    """
    if data_type == '.ascii':
        list_of_words = []  # A list to store a word (4 bytes)
        text = bytes()  # A list to store bytes and split them into words

        # loop over each char in the line, convert each 4 letters into bytes (1 word) and store them in list_of_bytes
        # then clear list_of_bytes and start again
        for i in range(len(line)):
            text += bytes(line[i], encoding='ascii')
            if len(text) % 4 == 0 or i == len(line) - 1:
                list_of_words += text.splitlines()
                text = bytes()

        writeOutDataBinary(list_of_words)  # Write the output into (.bin) file

    elif data_type == '.space':  # Leave some bytes empty
        writeOutDataBinary(bytes(int(line)))  # Write the output into (.bin) file

    else:  # Numeric data (either word or half or ... etc)
        list_of_words = list()
        for n in range(len(line)):
            list_of_words.append(int(line[n]).to_bytes(data_types[data_type]//4, byteorder='little'))

        writeOutDataBinary(list_of_words)  # Write the output into (.bin) file


def writeOutDataText():
    """
    A method that converts .bin file of data section into .txt file
    :return: None
    """
    # open the (.bin) file again to read from it
    f_obin = open('Binary_data.bin', 'rb')
    reading = f_obin.read()
    # Write the same binary data as text in the (.txt) file
    for i in range(0, len(reading), 4):
        f_text.write(
            myhdl.bin(int.from_bytes(reading[i:i + 4], 'little'), 32)
        )
        f_text.write('\n')
    # Close the two data files.
    f_obin.close()


def writeOutDataBinary(list_of_words):
    """
    A method that takes a list of words (4 bytes) from
    data section and writes it into .bin file
    :param list_of_words: a list containing 4 bytes
    :return: None
    """
    for word in list_of_words:
        f_bin.write(word)


def listInstrArgs(line) -> list:
    """
    :param line: line of instr and operands
    :return: list of operands without instr
    """
    args = list()
    words = line.split()
    for i in range(len(words)):
        if i == 0:
            continue
        args.append(words[i].replace(',', ''))
    return args


def replaceLabels(labels_locations: dict, lines: list) -> list:
    """
    A method that takes lines, and replace any label in there
    with the appropriate address corresponding to the label
    :param labels_locations: Dictionary with addres of each label
    :param lines: list of lines in the file
    :return: lines (the same list but with labels replaced by addresses)
    """
    for i in range(len(lines)):
        args = listInstrArgs(lines[i])
        for arg in args:
            if arg in labels_locations:
                lines[i] = lines[i].replace(arg, str(labels_locations[arg]))
            else:
                continue
    return lines


def replacePseudo(lines: list) -> list:
    # Process Pseudo instructions
    lines_real = list()
    count = text_start_address
    from Pseudo_code_converter import isPseudo, Pseudo_Converter
    for i, line in enumerate(lines):
        print('DEBUG LINE: '+line)
        first_word = line.split()[0].strip()
        if isPseudo(first_word) or isPseudo(line.strip()):
            print('DEBUG IS PSEUDO: ', first_word)
            args = listInstrArgs(line)
            args_padded = [0, 0, 0]
            print('DEBUG INST:', first_word, 'ARGS: ', args)
            for i in range(len(args)):
                args_padded[i] = args[i]
            if first_word == 'call':
                args_padded[0] = formatImm(args_padded[0])
                args_padded[0] = args_padded[0] - count
                args_padded[0] = int(intbv(int(args_padded[0]))[32:])
                args_padded[0] = "{0:032b}".format(args_padded[0])
            elif first_word == 'la':
                args_padded[1] = formatImm(args_padded[1])
                args_padded[1] = args_padded[1] - count
                args_padded[1] = int(intbv(int(args_padded[1]))[32:])
                args_padded[1] = "{0:032b}".format(args_padded[1])
            print('DEBUG PARSED ARGS', args_padded)
            converted = Pseudo_Converter(first_word, args_padded[0], args_padded[1], args_padded[2])
            print('DEBUG', converted, type(converted))
            if type(converted) == str:  # if a string then append directly to lines
        # TODO: this will go throgh branching insts and if the imm decimal value consists of 1s and 0s, it will convert.
                lines_real.append(convertBinImm2DecImm(converted))
                count += 4
            elif type(converted) == list or type(converted) == tuple:
                for entry in converted:
                    lines_real.append(convertBinImm2DecImm(entry))
                    count += 4
            elif isInstr(line):
                count += 4
            else:
                warn('Pseudo: Could not convert line: %s %s' % (line, type(converted)))
        else:
            lines_real.append(line)
    return lines_real


def getRegBin(reg) -> str:
    """
    A helper function that converts register representation into binary representation
    :param reg:
    :return:
    """
    if reg.startswith('x'):
        reg = reg.replace('x', '')
        return regs_bin[regsx[int(reg)]]
    else:
        if regs_bin[reg]:
            return regs_bin[reg]
        else:
            log('Unknown register', prefix='ERROR')
            return None


def formatImm(val: str) -> int:
    """
    Helper function that can recognize different representations of immediate and convert it into
    suitable integer representation
    :param val: string representation of immediate
    :return: integer representation for immediate
    """
    if val.startswith('0b'):
        val = val[2:]
        val = int(val, 2)
        return val
    elif val.startswith('0x'):
        val = val[2:]
        val = int(val, 16)
        return val
    else:
        try:
            val = int(val)
            return val
        except ValueError:
            log('Can not recognize imm value %s. Defaulting to zero' % val, prefix='ERROR')
            return 0


def isLabel(line) -> bool:
    """
    Helper function to decide whether the line is label or not
    :param line: Potential label
    :return: boolean (is the passed line a label?)
    """
    label_pattern = re.compile('[a-zA-Z0-9]+:')
    l = label_pattern.match(line)
    if not l:
        return False
    return True


def isInstr(line: str) -> bool:
    """
    A helper function to decide whether the line passed is an instruction or not
    :param line: A line that might contain an instruction
    :return: boolean (does the passed line contain an instruction?)
    """
    for word in line.split():
        for Instruction_type, instructions in all_instructions.items():
            for inst in instructions:
                if word == inst['inst']:
                    return True
    return False


def parseSTypeArgs(args: str) -> list:
    """
    Parse args of the style -100(sp) for example
    :return: A list of args in order of rs2, imm
    """
    args_out = list()
    general_pattern = re.compile("(-*[0-9]*\(\w\w\))")  # General pattern
    match1 = general_pattern.match(args)
    if match1:
        end = match1.end()
        reg_name = match1.group()[end - 3:end - 1]
        args_out.append(reg_name)
        imm = match1.group().replace('(' + reg_name + ')', '')
        if imm == '':
            # No Imm supplied
            imm = 0
        args_out.append(imm)
        log('Parsed S type with rs2: %s, imm: %s' % (reg_name, imm))
    else:
        #warn('Could not parse or match S type inst.')
        pass
    return args_out

# insts is a list of instructions in binary
def writeOutText(file_name: str, insts):
    # TODO make a check if file already exists and ask to overwrite. Now overwrites
    try:
        with open(file_name, 'w') as file:
            for inst in insts:
                file.write(inst.to_binary() + '\n')
        log('Done writing to %s' % file_name)
    except OSError as ex:
        log('Could not write assembled program. IO Error %s' % ex, 'ERROR')

# insts is a list of instructions in binary
def writeOutBinary(file_name: str, insts):
    with open(file_name, 'wb') as file:
        for inst in insts:
            val = int(inst.to_binary(), 2)
            file.write(val.to_bytes(4, 'little'))
    log('Done writing to %s' % file_name)


def parseArgs() -> dict:
    out_file_parser = argparse.ArgumentParser(add_help=False)
    out_file_parser.add_argument('-o', '--output', type=str, help='Output_file', metavar='Output_file', required=True)
    verbose_parser = argparse.ArgumentParser(add_help=False)
    verbose_parser.add_argument('-v', '--verbose', action='store_true')  # Could use count as level
    parser = argparse.ArgumentParser(parents=[out_file_parser, verbose_parser])
    parser.add_argument('input files', metavar='File_name', type=str, nargs='*')
    par = parser.parse_args()
    return vars(par)


def twos_comp(val, bits):
    """
    A helper function that calculates two's complement
    :param val: number to find two's comp of
    :param bits: number of bits
    :return: two's complement
    """
    if (val & (1 << (bits - 1))) != 0:
        val = val - (1 << bits)
    return val


def validArgs(args):
    if len(args['input files']) == 0:
        return 'Provide at least one input file'

    for file_name in args['input files']:
        if not file_name.endswith('.asm'):
            return 'Provide files with asm extension'

    out_file_name = args['output']
    if not (out_file_name.endswith('.txt') or out_file_name.endswith('.bin')):
        return 'Output file format must be selected [txt or bin]'
    return None


def stripEscapeChars(lines: list) -> list:
    """
    A helper function that cleans a list of lines from unwanted characters
    :param lines: A list of lines to be cleaned
    :return: cleaned list of lines
    """
    cleared_lines = list()
    for line in lines:
        line_mod = line.replace('\t', ' ')
        line_mod = line_mod.strip('\n')
        line_mod = line_mod.strip('\t')
        line_mod = line_mod.strip()
        if len(line_mod) < 1:
            continue
        cleared_lines.append(line_mod)
    return cleared_lines


def convertBinImm2DecImm(line: str) -> str:
    words = line.split()
    line_mod = line
    for i, word in enumerate(words):
        try:
            val = int(word, 2)
            line_mod = line_mod.replace(word, str(val))
        except ValueError as ex:
            pass
    return line_mod


def log(msg, prefix: str = 'INFO'):
    if verbose or prefix == 'ERROR':
        print("[%s] %s" % (prefix, msg))


def warn(msg):
    log(msg, prefix="WARNNING")


def debug(msg):
    log(msg, prefix="DEBUG")


if __name__ == '__main__':
    exit(main())
