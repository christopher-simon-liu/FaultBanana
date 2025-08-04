#!/bin/bash

# 32-bit ARM
python ../Scripts/deep_simulate_faults.py ./pin-verify.o ./critical_mutants.json . arm_32 10
