#!/usr/bin/env python

import sys

print("RISC-V RV32IM assembler (Team 2)")


def main():
    output_file_name = ''
    for i in range(len(sys.argv)):
        if sys.argv[i] == '-o' and len(sys.argv) >= i+1:
            output_file_name = sys.argv[i+1]


if __name__ == '__main__':
    exit(main())
