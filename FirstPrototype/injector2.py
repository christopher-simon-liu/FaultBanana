# Required imports
import mmap
import sys, getopt
import os
import argparse
from argparse import RawTextHelpFormatter,SUPPRESS
import json

def SanityCheck(values, position, instruction):
    sane = True
    size = len(instruction)
    original = []
    for i in range(size):
        index = position + i
        if values[index] != instruction[i]:
            sane = False
        original.append(values[index])
    # print(f"original: {original}")
    return sane

def ReplaceBytes(values, outfile, position, instruction):
    size = len(instruction)
    original = []
    for i in range(size):
        index = position + i
        values[index] = instruction[i]
    store = open(outfile, 'wb')
    store.write(values)
    store.close()
    

def main():  
    ## entry point of this program
    ## Parsing the arguments
    parser = argparse.ArgumentParser(description="Tool Options")
    parser.add_argument("binary", default="./motivating.o", type=str, help="Path to binary.o")
    parser.add_argument("offset", default=40, type=int, help="Starting binary byte index")
    parser.add_argument("size", default=124, type=int, help="Size of .text section")
    parser.add_argument("snippets", default="./snippets.json", type=str, help="Path to instruction snippets.json")
    parser.add_argument("out", default="./critical_mutants", type=str, help="Path to output folder")
    parser.add_argument("--fm", default="reset", type=str, help="Fault Model (set, reset, flip)")

    args = parser.parse_args()
    binary_path = args.binary
    offset = args.offset
    textsize = args.size
    snippets_path = args.snippets
    out_path = args.out
    fault_model = args.fm

    file_name = os.path.basename(binary_path)
    name = os.path.splitext(file_name)[0]

    byte_array = []
    try:
        with open(binary_path, "r+b") as f:
            mm = mmap.mmap(f.fileno(), 0)
            byte_array = bytearray(mm)
            sizefile=len(byte_array)
            print(f"{sizefile} bytes")
            f.close()
    except FileNotFoundError:
        print(f"Error: The file '{binary_path}' was not found.")
    
    snippets = {}
    try:
        with open(snippets_path, 'r') as s:
            snippets = json.load(s)
            s.close()
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{file_path}'. Check for valid JSON format.")

    for index in snippets.keys():
        i_index = int(index)
        if i_index <= textsize:
            print(f"Sanity check: instruction index {index} in .text? True")
            original = snippets[index]["original"]
            mutants = snippets[index]["mutants"]
            
            original_bytes = [int(s) for s in snippets[index]["original"].split()]
            # print(f"original?: {original_bytes}")

            position = i_index + offset
            print(f"Sanity check: instruction bytes match original? {SanityCheck(byte_array, position, original_bytes)}")

            for mutant in mutants.keys():
                mutant_bytes = [int(s) for s in mutant.split()]
                offsets = mutants[mutant].strip().replace(" ", "_")

                mutant_file = os.path.join(out_path, f"{name}-{index}-{fault_model}-{offsets}.o")
                binary_to_mutate = byte_array.copy()
                ReplaceBytes(binary_to_mutate, mutant_file, position, mutant_bytes)

                print(f"{mutant_file} created")
        else:
            print(f"Sanity check: instruction index {index} in .text? False")
            continue

if __name__ == "__main__":
    main()

# mkdir -p ./critical_mutants/x86-32/reset
# python ../injector2.py ./m32.o 60 297 ./snippets/x86-32/snippets-x86-32-reset.json ./critical_mutants/x86-32/reset --fm reset