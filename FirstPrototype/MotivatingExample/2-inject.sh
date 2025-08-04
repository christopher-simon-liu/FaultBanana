#!/bin/bash

# 32-bit x86
mkdir -p ./mutants/set
python ../injector.py ./m32.o 60 336 ./mutants/set --fm set
mkdir -p ./mutants/reset
python ../injector.py ./m32.o 60 336 ./mutants/reset --fm reset
mkdir -p ./mutants/flip
python ../injector.py ./m32.o 60 336 ./mutants/flip --fm flip

# $python ../objdump-h.py ./m32.o
# Process completed with exit code: 0
# Size:
# 336
# Offset:
# 60