#!/bin/bash

# 32-bit x86
python ../Scripts/deep_simulate_faults.py ./pin-verify.o ./critical_mutants.json . i386 10
