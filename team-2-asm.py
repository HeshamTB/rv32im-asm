#!/usr/bin/env python

import sys, argparse

print("RISC-V RV32IM assembler (Team 2)")


def main():
    args = parseArgs()
    err = validArgs(args)
    if err is not None:
        print(err)
        return 2
    print("Assembly file: %s" % args['input files'])


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
            return 'Provide files with asm extention'

    return None



if __name__ == '__main__':
    exit(main())
