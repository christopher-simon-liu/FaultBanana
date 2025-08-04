#!/bin/bash

# 32-bit x86
mkdir -p ./parse/
python ../objdump-p.py ./disassemble/m32.asm ./m32.o 60 336 ./parse/ --t i386