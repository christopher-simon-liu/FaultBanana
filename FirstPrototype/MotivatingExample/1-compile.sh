#!/bin/bash

# 32-bit x86
gcc -m32 -c -g -O0 -o m32.o motivating.c 

# gcc -c compile and assemble but don't link
# gcc -g -O0 compile with debug info 
# without optimization so assembly matches C more directly
