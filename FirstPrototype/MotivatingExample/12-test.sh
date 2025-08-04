#!/bin/bash

# 32-bit x86
mkdir -p ./critical_outputs/set
python ../tester-a.py ./critical_linked/set ./critical_outputs/set i386 10 ./critical_linked/set/original/m32.o

mkdir -p ./critical_outputs/reset
python ../tester-a.py ./critical_linked/reset ./critical_outputs/reset i386 10 ./critical_linked/reset/original/m32.o

mkdir -p ./critical_outputs/flip
python ../tester-a.py ./critical_linked/flip ./critical_outputs/flip i386 10 ./critical_linked/flip/original/m32.o