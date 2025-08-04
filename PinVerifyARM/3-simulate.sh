#!/bin/bash

# 32-bit ARM
python ../Scripts/quick_simulate_faults.py ./pin-verify.o ./mutants.json . arm_32 10
