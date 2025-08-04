#!/bin/bash

# 32-bit x86
mkdir -p ./outputs/set
python ../tester-a.py ./linked/set ./outputs/set i386 10 ./linked/set/original/m32.o

mkdir -p ./outputs/reset
python ../tester-a.py ./linked/reset ./outputs/reset i386 10 ./linked/reset/original/m32.o

mkdir -p ./outputs/flip
python ../tester-a.py ./linked/flip ./outputs/flip i386 10 ./linked/flip/original/m32.o