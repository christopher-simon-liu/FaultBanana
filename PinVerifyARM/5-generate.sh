#!/bin/bash

# 32-bit ARM
python ../Scripts/deep_generate_faults.py ./pin-verify.o 52 260 . arm_32

# .text section:
#          Size: 260
#          Offset: 52 
