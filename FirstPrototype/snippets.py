import mmap
import sys, getopt
import os
import argparse
from argparse import RawTextHelpFormatter,SUPPRESS
import csv
import json

def ResetFault(offset, binary_string):
    binary_list = list(binary_string)
    for i in range(8):
        index = i + offset
        binary_list[index] = "0"
    
    return "".join(binary_list)

def SetFault(offset, binary_string):
    binary_list = list(binary_string)
    for i in range(8):
        index = i + offset
        binary_list[index] = "1"
    
    return "".join(binary_list)

def FlipFault(offset, binary_string):
    binary_list = list(binary_string)
    for i in range(8):
        index = i + offset
        temp = binary_list[index]
        if temp == "0":
            binary_list[index] = "1"
        else:
            binary_list[index] = "0"
    
    return "".join(binary_list)

def BinaryToByteInt(binary_string):
    binary_list = list(binary_string)
    int_string = ""
    for i in range(0, len(binary_list), 8):
        byte_string = ""
        for j in range(8):
            index = i + j
            byte_string = byte_string + binary_list[index]
        int_string = int_string + " " + str(int(byte_string, 2))
    return int_string.strip()

def IntToByteBinary(int_string):
    int_list = int_string.split()
    binary_list = [bin(int(i))[2:].zfill(8) for i in int_list]
    big_binary = "".join(binary_list)
    return big_binary

def main():  
    ## entry point of this program
    ## Parsing the arguments
    parser = argparse.ArgumentParser(description="Tool Options")
    parser.add_argument("critical", default="./critical-x86-32-reset.csv", type=str, help="Path to critical.csv")    
    parser.add_argument("name", default="x86-32", type=str, help="identifier")
    parser.add_argument("out", default="./", type=str, help="Path to output folder")
    parser.add_argument("--fm", default="reset", type=str, help="Fault Model (set, reset, flip)")

    args = parser.parse_args()
    critical_path = args.critical
    name = args.name
    out_path = args.out
    fault_model = args.fm

    binary_snippets = {}

    with open(critical_path, "r") as file:
        csvFile = csv.reader(file)
        for line in csvFile:
            index = line[0]
            int_string = line[1].replace("[", "").replace("]", "").replace(",", "")
            print(int_string)
            
            big_binary = IntToByteBinary(int_string)

            print(f"Instruction {index}")
            print(f"Original Bytes: {int_string}")
            print(big_binary)

            total_offsets = len(big_binary) - 8 + 1
            print(f"Possible offsets: {total_offsets}")

            mutants = {}
            for i in range(total_offsets):
                mutant = ""
                if fault_model == "flip":
                    mutant = FlipFault(i, big_binary)
                elif fault_model == "set":
                    mutant = SetFault(i, big_binary)
                else: # reset zero byte fault model
                    mutant = ResetFault(i, big_binary)
                print(f"mutant{i}: {mutant}")
                mutant_int_string = BinaryToByteInt(mutant)
                if mutant_int_string in mutants.keys():
                    mutants[mutant_int_string] = mutants[mutant_int_string] + " " + str(i)
                else:
                    mutants[mutant_int_string] = str(i)
            print(mutants)
            binary_snippets[index] = {
                "original": int_string,
                "mutants": mutants
            }
        file.close()

    out_file_path = os.path.join(out_path, f"snippets-{name}-{fault_model}.json")

    with open(out_file_path, "w") as f:
        f.write(json.dumps(binary_snippets, indent=2))
        f.close()

    print(f"{out_file_path} created")


if __name__ == "__main__":
    main()

# python ../snippets.py ./critical-x86-32-reset.csv x86-32 --fm reset