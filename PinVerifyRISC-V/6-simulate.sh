#!/bin/bash

# 32-bit RISC-V
python ../Scripts/deep_simulate_faults.py ./pin-verify.o ./critical_mutants.json . riscv32 10
