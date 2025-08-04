#!/bin/bash

# 32-bit RISC-V
python ../Scripts/quick_simulate_faults.py ./pin-verify.o ./mutants.json . riscv32 10
