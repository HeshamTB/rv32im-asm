#!/usr/bin/env python

import argparse, re
import Instructions

print("RISC-V RV32IM assembler (Team 2)")
verbose = False
# Following RARS Simulator
text_start_address = 0x00400000
date_start_address = 0x10010000


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
    for line in in_lines:
        line = line.strip()
        if not line or line.startswith('#'):
            pass

    for i in range(len(in_lines)):
        in_lines[i] = in_lines[i].strip()
        in_lines[i] = re.sub(r'(^[ \t]+|[ \t]+(?=:))', '', in_lines[i], flags=re.M)
        log('{} {}'.format(hex(i), in_lines[i].split()))
        if not in_lines[i].split():
            continue
        # in_words.append(in_lines[i].split())
        # not efficient, refactor
        for inst_type, instructions in Instructions.all_instructions.items():
            for instruction in instructions:
                word = in_lines[i].split()[0]
                if word == instruction['inst']:
                    print("Found", word, instruction['inst'])
                    out_binary_string.append(
                        Instructions.Instruction(instruction['inst']))

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
            label = poten_label.group()
            label.replace(':', '')  # Remove trailing colon 'label:' -> 'label'
            # Add label with address+4 since nothing should be after the label. We hope.
            label_mapping[label] = address + 0x04
        else:
            address += 0x04  # Not a label
    return label_mapping


def parseArgs():
    out_file_parser = argparse.ArgumentParser(add_help=False)
    out_file_parser.add_argument('-o', '--output', type=str, help='Output_file', metavar='Output_file', required=True)
    verbose_parser = argparse.ArgumentParser(add_help=False)
    verbose_parser.add_argument('-v', '--verbose', action='store_true')  # Could use count as level
    parser = argparse.ArgumentParser(parents=[out_file_parser, verbose_parser])
    parser.add_argument('input files', metavar='File_name', type=str, nargs='*')
    par = parser.parse_args()
    return vars(par)


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


def log(*msg, prefix='INFO'):
    if verbose or prefix == 'ERROR':
        print("[%s]" % prefix, msg)


if __name__ == '__main__':
    exit(main())
