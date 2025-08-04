#!/bin/bash

# 32-bit x86
python ../visualizer.py ./outputs/set ./mutants/set Fault-Banana-m32-set > ./Fault-Banana-m32-set.txt

python ../visualizer.py ./outputs/reset ./mutants/reset Fault-Banana-m32-reset > ./Fault-Banana-m32-reset.txt

python ../visualizer.py ./outputs/flip ./mutants/flip Fault-Banana-m32-flip > ./Fault-Banana-m32-flip.txt