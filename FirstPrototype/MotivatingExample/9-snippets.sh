#!/bin/bash

# 32-bit x86
mkdir -p ./snippets/set
python ../snippets.py ./isolate/set/critical-m32-set.csv m32 ./snippets/set --fm set
mkdir -p ./snippets/reset
python ../snippets.py ./isolate/reset/critical-m32-reset.csv m32 ./snippets/reset --fm reset
mkdir -p ./snippets/flip
python ../snippets.py ./isolate/flip/critical-m32-flip.csv m32 ./snippets/flip --fm flip

