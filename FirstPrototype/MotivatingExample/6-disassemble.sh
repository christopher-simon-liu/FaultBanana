#!/bin/bash

# 32-bit x86
mkdir -p ./disassemble/
python ../objdump-d.py ./m32.o ./disassemble/ --d i386
