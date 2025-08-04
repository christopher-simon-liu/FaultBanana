#!/bin/bash

# 32-bit x86
mkdir -p ./linked/set/original
python ../linker.py ./mutants/set ./linked/set i386 ./m32.o

mkdir -p ./linked/reset/original
python ../linker.py ./mutants/reset ./linked/reset i386 ./m32.o

mkdir -p ./linked/flip/original
python ../linker.py ./mutants/flip ./linked/flip i386 ./m32.o