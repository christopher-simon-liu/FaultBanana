#!/bin/bash

# 32-bit x86
# gcc -m32 -c -g -O0 -o ./pin-verify.o ../Case-Studies/pin-verify.c 
python ../compile_binary.py ../Case-Studies/pin-verify.c ./pin-verify.o i386

# gcc -c compile and assemble but don't link
# gcc -g -O0 compile with debug info 
# without optimization so assembly matches C more directly

# python ../find_section.py ./pin-verify.o
# .text section:
#          Size: 284
#          Offset: 60
