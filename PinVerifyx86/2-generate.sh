#!/bin/bash

# 32-bit x86
python ../Scripts/quick_generate_faults.py ./pin-verify.o 60 284 .

# .text section:
#          Size: 284
#          Offset: 60