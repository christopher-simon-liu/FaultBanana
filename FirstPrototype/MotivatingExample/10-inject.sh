#!/bin/bash

# 32-bit x86
mkdir -p ./critical_mutants/set
python ../injector2.py ./m32.o 60 336 ./snippets/set/snippets-m32-set.json ./critical_mutants/set --fm set

mkdir -p ./critical_mutants/reset
python ../injector2.py ./m32.o 60 336 ./snippets/reset/snippets-m32-reset.json ./critical_mutants/reset --fm reset

mkdir -p ./critical_mutants/flip
python ../injector2.py ./m32.o 60 336 ./snippets/flip/snippets-m32-flip.json ./critical_mutants/flip --fm flip