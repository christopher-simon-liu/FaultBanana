#!/bin/bash

# 32-bit x86
mkdir -p ./critical_linked/set/original
python ../linker.py ./critical_mutants/set ./critical_linked/set i386 ./m32.o

mkdir -p ./critical_linked/reset/original
python ../linker.py ./critical_mutants/reset ./critical_linked/reset i386 ./m32.o

mkdir -p ./critical_linked/flip/original
python ../linker.py ./critical_mutants/flip ./critical_linked/flip i386 ./m32.o