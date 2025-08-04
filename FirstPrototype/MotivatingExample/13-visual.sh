#!/bin/bash

# 32-bit x86
mkdir -p ./critical_images/set
python ../visualizer2.py ./critical_outputs/set ./critical_mutants/set Critical-Fault-Banana-m32-set ./critical_images/set ./parse/m32.json ./m32.o ./snippets/set/snippets-m32-set.json > ./Critical-Fault-Banana-m32-set.txt

mkdir -p ./critical_images/reset
python ../visualizer2.py ./critical_outputs/reset ./critical_mutants/reset Critical-Fault-Banana-m32-reset ./critical_images/reset ./parse/m32.json ./m32.o ./snippets/reset/snippets-m32-reset.json > ./Critical-Fault-Banana-m32-reset.txt

mkdir -p ./critical_images/flip
python ../visualizer2.py ./critical_outputs/flip ./critical_mutants/flip Critical-Fault-Banana-m32-flip ./critical_images/flip ./parse/m32.json ./m32.o ./snippets/flip/snippets-m32-flip.json > ./Critical-Fault-Banana-m32-flip.txt