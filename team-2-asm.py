#!/usr/bin/env python

import argparse

print("RISC-V RV32IM assembler (Team 2)")
verbose = False


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

    in_lines = list()
    with open(in_file_name, 'r') as in_file:
        in_lines = in_file.readlines()
    for line in in_lines:
        line.strip()
        if line.startswith("#"):
            in_lines.remove(line)
    # For testing. To be removed/changed
    for i in range(len(in_lines)):
        print(hex(i), in_lines[i])


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


def log(msg, prefix='INFO'):
    if verbose or prefix == 'ERROR':
        print("[%s]" % prefix, msg)


if __name__ == '__main__':
    exit(main())
