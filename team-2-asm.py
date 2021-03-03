#!/usr/bin/env python

import argparse, re
from Instructions import Instruction, all_instructions
from myhdl import intbv

print("RISC-V RV32IM assembler (Team 2)")
verbose = False
# Following RARS Simulator
text_start_address = 0x00400000
data_start_address = 0x10010000
regs = ['zero', 'ra', 'sp', 'gp', 'tp', 't0', 't1', 't2', 's0', 's1',
        'a0', 'a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 's2', 's3', 's4',
        's5', 's6', 's7', 's8', 's9', ' s10', 's11', 't3', 't4', 't5', 't6', 'pc']
regs_bin = dict()
for i in range(len(regs)):
    regs_bin[regs[i]] = "{0:05b}".format(i)


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

    # Split to into methods and modules
    in_lines = list()
    out_binary_string = list()
    with open(in_file_name, 'r') as in_file:
        in_lines = in_file.readlines()

    in_lines = stripEscapeChars(in_lines)
    labels = calculateLabels(in_lines, 'text')
    log(labels)
    in_lines = replaceLabels(labels, in_lines)
    print(in_lines)
    address = text_start_address  # Account for data sec
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
                            rd = getRegBin(args[0])
                            rs1 = getRegBin(args[1])
                            imm = formatImm(args[2])
                            imm = intbv(imm, max=4095)[12:]
                            imm_delta_bin = int(intbv(int(imm), max=4095)[12:])  # TODO improper sign ext. (00011111)
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
                        rs1 = getRegBin(args[0])
                        rs2 = getRegBin(args_s[0])
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
                        imm = int(intbv(imm)[20:])
                        imm = "{0:020b}".format(imm)
                        log('PC: %s, inst: %s, rd: %s, imm: %s' % (address, inst, rd, imm))
                        out_binary_string.append(Instruction(
                            instr=inst,
                            rd=rd,
                            imm=imm
                        ))
                    elif inst_type == 'J':
                        #  This assumes a reg is provided (jal ra, label_add)
                        rd = getRegBin(args[0])
                        imm = formatImm(args[1])
                        imm = int(intbv(imm)[21:])
                        imm = "{0:021b}".format(imm)
                        log('PC: %s, inst: %s, rd: %s, imm: %s' % (address, inst, rd, imm))
                        out_binary_string.append(Instruction(
                            instr=inst,
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


def calculateLabels(lines) -> dict:
    """
     Calculate address for each label in lines
     :returns dict with 'label:' : address
     This assumes all instructions are real RISC-V 32-bit instructions.
     Thus, adding 4 between each instruction.
    """
    address = 0
    section = 'text'  # default section
    label_pattern = re.compile('[a-zA-Z0-9]+:')
    directive_pattern = re.compile('.+[a-zA-Z]')  # make this ignore what comes after the first space

    label_mapping = dict()
    for i in range(len(lines)):
        # if lines[i].startswith('.'):
        if lines[i] == '.data':
            address = data_start_address
            section = 'data'

        elif lines[i] == '.text':
            address = text_start_address
            section = 'text'

        if section == 'text':
            poten_label = label_pattern.match(lines[i])
            if poten_label:
                label = poten_label.group().replace(':', '')
                # Add label with address+4 since nothing should be after the label. We hope.
                if address == text_start_address:  # or address == 0:  # First line is diff
                    label_mapping[label] = address
                else:
                    label_mapping[label] = address + 4
                # log("(%s) @ %s" % (label, hex(address)))
            elif isInstr(lines[i]):
                address += 4  # Not a label


        # the rules for data segment:
        #   1- format is [label: .data_type data]
        #   2- if data consist of numbers, is should be seperated by commas
        #   3- in case of commas, there must be a space after it
        #   4- if data consist of string, it must be contained in " "
        #   5- all of the above must be in one line

        # Next step: dictionary for data types and increment address based on that, and write output.

        elif section == 'data':
            poten_label = label_pattern.match(lines[i])
            if (poten_label):
                data_label = poten_label.group().replace(':', '').strip()
                mod_line = lines[i].replace(data_label + ':', '').strip()
                poten_dir = directive_pattern.match(mod_line)
                if not poten_dir:
                    print("Error")
                    exit(0)
                # the split in next line will get rid of whatever after the first word
                data_type = poten_dir.group().split(' ', 1)[0]
                mod_line = mod_line.replace(data_type, '').strip()
                print(data_label)
                print(data_type)
                print(mod_line)
                # print(poten_label.group())

    # log('Located and mapped labels %s' % label_mapping)
    return label_mapping

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


def replaceLabels(labels_locations : dict, lines : list) -> list:
    for i in range(len(lines)):
        args = listInstrArgs(lines[i])
        for arg in args:
            if arg in labels_locations:
                lines[i] = lines[i].replace(arg, str(labels_locations[arg]))
            else:
                continue

    return lines


def getRegBin(reg) -> str:
    if reg.startswith('x'):
        reg = reg.replace('x', '')
        return regs_bin[regs[reg]]
    else:
        if regs_bin[reg]:
            return regs_bin[reg]
        else:
            log('Unknown register', prefix='ERROR')
            return None


def formatImm(val: str) -> int:
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
    label_pattern = re.compile('[a-zA-Z0-9]+:')
    l = label_pattern.match(line)
    if not l:
        return False
    return True


def isInstr(line: str) -> bool:
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
        warn('Could not parse or match S type inst.')
    return args_out


def writeOutText(file_name: str, insts: list[Instruction]):
    # TODO make a check if file already exists and ask to overwrite. Now overwrites
    with open(file_name, 'w') as file:
        for inst in insts:
            file.write(inst.to_binary() + '\n')
    log('Done writing to %s' % file_name)


def writeOutBinary(file_name: str, insts: list[Instruction]):
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


def stripEscapeChars(lines) -> list:
    cleared_lines = list()
    for line in lines:
        line_mod = line.replace('\t', ' ')
        line_mod = line_mod.strip('\n')
        line_mod = line_mod.strip()
        if len(line_mod) <1:
            continue
        cleared_lines.append(line_mod)
    return cleared_lines


def log(msg, prefix: str = 'INFO'):
    if verbose or prefix == 'ERROR':
        print("[%s] %s" % (prefix, msg))


def warn(msg):
    log(msg, prefix="WARNNING")


if __name__ == '__main__':
    exit(main())
