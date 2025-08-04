#!/bin/bash

# 32-bit RISC-V
python ../Scripts/quick_generate_faults.py ./pin-verify.o 52 256 .

# .text section:
#          Size: 256
#          Offset: 52
