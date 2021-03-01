#!/usr/bin/env python

import argparse, re
import Instructions
from Instructions import Instruction, all_instructions

print("RISC-V RV32IM assembler (Team 2)")
verbose = False
# Following RARS Simulator
text_start_address = 0x00400000
date_start_address = 0x10010000
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
    address = text_start_address
    for i in range(len(in_lines)):
        in_lines[i] = in_lines[i].strip()
        if not in_lines[i].split() or isLabel(in_lines[i]):
            continue
        # in_words.append(in_lines[i].split())
        # not efficient, refactor
        for inst_type, instructions in all_instructions.items():
            for instruction in instructions:
                word = in_lines[i].split()[0]
                if word == instruction['inst']:
                    log('%s %s' % (hex(address), word))
                    args = listInstrArgs(in_lines[i])
                    # if not args: continue
                    inst = instruction['inst']
                    print(args)
                    if inst_type == 'R':
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
                            imm = formatImm(args[2], 12)
                            imm = "{0:012b}".format(int(imm))
                            log('rd: %s, rs1: %s, imm: %s' % (rd, rs1, imm))
                            out_binary_string.append(
                                Instruction(instr=inst,
                                            frmt=inst_type,
                                            rd=rd,
                                            rs1=rs1,
                                            imm=imm,
                                            func3=instruction['func3']))
                    elif inst_type == 'S':
                        continue
                    elif inst_type == 'B': # Reg, Reg, Address
                        rs1 = getRegBin(args[0])
                        rs2 = getRegBin(args[1])
                        imm = formatImm(args[2], 32) # Here the value is abs Address. From ISA PC += imm. imm is distance
                        delta = address - imm << 1 # TODO check bit 0
                        print("delta", hex(delta))
                        # TODO check if delta is higher then 12-bits
                        imm = "{0:012b}".format(delta)
                        print('Delta bin', imm)
                        out_binary_string.append(
                            Instruction(instr=inst,
                                        frmt=inst_type,
                                        rs1=rs1,
                                        rs2=rs2,
                                        imm=imm,
                                        func3=instruction['func3']))
                    else:
                        continue
                    address += 4

    for entry in out_binary_string:
        print(entry.to_binary())


def calculateLabels(lines, section) -> dict:
    """
     Calculate address for each label in lines
     :returns dict with 'label:' : address
     This assumes all instructions are real RISC-V 32-bit instructions.
     Thus, adding 4 between each instruction.
    """
    address = date_start_address
    label_pattern = re.compile('[a-zA-Z0-9]+:')
    label_mapping = dict()
    if section == 'data':
        address = date_start_address
    else:
        address = text_start_address
    for i in range(len(lines)):
        poten_label = label_pattern.match(lines[i])
        if poten_label:
            label = poten_label.group().replace(':', '')
            # Add label with address+4 since nothing should be after the label. We hope.
            label_mapping[label] = address + 0x04
            # log("(%s) @ %s" % (label, hex(address)))
        else:
            address += 0x04  # Not a label
    log('Located and mapped labels %s' % label_mapping)
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


def replaceLabels(labels_locations, lines) -> list:
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


def formatImm(val, bits):
    if val.startswith('0b'):
        val = val[2:]
        val = int(val, 2)
        return twos_comp(val, bits)
    elif val.startswith('0x'):
        val = val[2:]
        val = int(val, 16)
        return twos_comp(val, bits)
    else:
        try:
            val = int(val)
            return twos_comp(val, bits)
        except ValueError:
            log('Can not recognize imm value %s. Defaulting to zero' % val, prefix='ERROR')
            return 0


def isLabel(line) -> bool:
    label_pattern = re.compile('[a-zA-Z0-9]+:')
    l = label_pattern.match(line)
    if not l:
        return False
    return True


def parseArgs():
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
        line_mod = line.strip('\n')
        line_mod = line_mod.strip('\t')
        cleared_lines.append(line_mod)
    return cleared_lines


def log(msg, prefix='INFO'):
    if verbose or prefix == 'ERROR':
        print("[%s] %s" % (prefix, msg))


if __name__ == '__main__':
    exit(main())
