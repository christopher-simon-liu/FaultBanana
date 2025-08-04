#!/bin/bash

# 32-bit x86
python ../Scripts/deep_generate_faults.py ./pin-verify.o 60 284 . i386

# .text section:
#          Size: 284
#          Offset: 60
