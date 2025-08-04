#!/bin/bash

# 32-bit ARM
python ../compile_binary.py ../Case-Studies/pin-verify.c ./pin-verify.o arm_32

# gcc -c compile and assemble but don't link
# gcc -g -O0 compile with debug info 
# without optimization so assembly matches C more directly

# python ../find_section.py ./pin-verify.o
# .text section:
#          Size: 260
#          Offset: 52 
