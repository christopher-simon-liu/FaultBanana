#!/bin/bash

# 32-bit x86
mkdir -p ./isolate/set
python ../isolate.py ./Fault-Banana-m32-set.txt ./parse/m32.json ./m32.o m32-set ./isolate/set

mkdir -p ./isolate/reset
python ../isolate.py ./Fault-Banana-m32-reset.txt ./parse/m32.json ./m32.o m32-reset ./isolate/reset

mkdir -p ./isolate/flip
python ../isolate.py ./Fault-Banana-m32-flip.txt ./parse/m32.json ./m32.o m32-flip ./isolate/flip

