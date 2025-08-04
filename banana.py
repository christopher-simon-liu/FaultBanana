#!/bin/python
import os
import sys
import argparse
import subprocess
import json

bio = """
 Binary Fault Banana
 Author: Christopher Simon Liu
 Contact: liu.8689@osu.edu 
"""
title = r"""
 ______          _ _     ____                                
|  ____|        | | |   |  _ \                               
| |__ __ _ _   _| | |_  | |_) | __ _ _ __   __ _ _ __   __ _ 
|  __/ _` | | | | | __| |  _ < / _` | '_ \ / _` | '_ \ / _` |
| | | (_| | |_| | | |_  | |_) | (_| | | | | (_| | | | | (_| |
|_|  \__,_|\__,_|_|\__| |____/ \__,_|_| |_|\__,_|_| |_|\__,_|                                                           
"""
banana = r"""
 _
//\
V  \
 \  \_
  \,'.`-.
   |\ `. `.       
   ( \  `. `-.                        _,.-:\
    \ \   `.  `-._             __..--' ,-';/
     \ `.   `-.   `-..___..---'   _.--' ,'/
      `. `.    `-._        __..--'    ,' /
        `. `-_     ``--..''       _.-' ,'
          `-_ `-.___       __,--'   ,'
             `-.__  `----""    __.-'
"""
tips = """
Tips on creating an input binary:

gcc -c -g -O0 -o <binary.o> <source.c>
(-c)  turns off library linking so only the source is compiled
(-g)  turns on debug info for disassembly
(-O0) turns off optimization so assembly matches C more directly

- different compilers and objdumps are needed for different architectures
- make sure the code has an assert statement to detect attacks on logic
"""
def run(command):
    result = None
    try:
        result = subprocess.run([command], shell=True, check=True)
        print("Command completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Command failed with an error: {e}")
    return result

def main():
    ## entry point of this program
    print(banana)
    print(title)
    print("*"*42)
    print(bio)
    print("*"*42)
    print(tips)
    print("*"*42)

    binary_path = "./test.o"
    target_architecture = "i386"
    out_path = "./out"
    timeout = 10
    offset = 0
    size = 100
    ready = False

    while not ready:
        binary_path = input("Enter the path to the binary (ex: ./test.o): ")
        offset_num = input("Enter the byte offset of the binary section (ex: .text) of interest (ex: 0): ")
        size_num = input("Enter the byte size of the binary section (ex: .text) of interest (ex: 100): ")
        target_architecture = input("Enter the target architecture (ex: x86_64, i386, arm_32, riscv32): ")
        out_path = input("Enter the path to the output folder (ex: ./out): ")
        time_out = input("Enter the timout seconds (ex: 10): ")
        ready_check = input("This might take a while... Ready? (yes/no): ")
        
        offset = int(offset_num)
        size = int(size_num)
        timeout = int(time_out)

        if "y" in ready_check:
            ready = True
  
    # "Quick" Analysis

    run(f"python ./Scripts/quick_generate_faults.py {binary_path} {offset} {size} {out_path}")
    mutants_path = os.path.join(out_path, f"mutants.json")
    run(f"python ./Scripts/quick_simulate_faults.py {binary_path} {mutants_path} {out_path} {target_architecture} {timeout}")
    run(f"python ./Scripts/quick_visualize_faults.py {mutants_path} {out_path}")

    # "Deep" Analysis

    run(f"python ./Scripts/deep_generate_faults.py {binary_path} {offset} {size} {out_path} {target_architecture}")
    critical_mutants_path = os.path.join(out_path, f"critical_mutants.json")
    run(f"python ./Scripts/deep_simulate_faults.py {binary_path} {critical_mutants_path} {out_path} {target_architecture} {timeout}")
    run(f"python ./Scripts/deep_visualize_faults.py {critical_mutants_path} {out_path}")
    
    return 0

if __name__ == "__main__":
    main()
