#!/bin/bash

# 32-bit ARM
python ../Scripts/quick_generate_faults.py ./pin-verify.o 52 260 .

# .text section:
#          Size: 260
#          Offset: 52 
