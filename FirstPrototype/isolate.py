import os
import sys
import argparse
import subprocess
import json

"""
Function FindIndexImpacted(sussy_index, instruction_indexes)
	* Finds the impacted instruction
    * check if a sussy index is more than or equal to a starting index
    * check if a sussy index is less than the next starting index
"""
def FindIndexImpacted(sussy_index, instruction_indexes):
    length = len(instruction_indexes)
    i = 0
    j = 1
    while i < length -1:
        start_index = instruction_indexes[i]
        next_index = instruction_indexes[j]
        if (start_index <= sussy_index and sussy_index < next_index):
            return start_index
        i += 1
        j += 1
    return -1

def main():
    ## entry point of this program
    ## Parsing the arguments
    parser = argparse.ArgumentParser(description="Tool Options")
    parser.add_argument("banana", default="./Fault-Banana-x86-32-reset.txt", type=str, help="Path to banana.txt file")
    parser.add_argument("debug", default="./m32.json", type=str, help="Path to json file with assembly debugging info")
    parser.add_argument("binary", default="./m32.o", type=str, help="Path to binary.o")
    parser.add_argument("name", default="x86-32-reset", type=str, help="identifier")
    parser.add_argument("out", default="./", type=str, help="Path to output folder")

    args = parser.parse_args()
    banana_path = args.banana
    debug_path = args.debug
    binary_path = args.binary
    name = args.name
    out_path = args.out

    sussy_indexes = []
    try:
        with open(banana_path, 'r') as file:
            for line in file:
                if "Sussy" in line:
                    sussy = line.replace("Sussy:", "").strip()
                    numbers = sussy.replace("[", "").replace("]", "")
                    data = numbers.split(', ')
                    integer_list = [int(s) for s in data]
                    integer_list.sort()
                    sussy_indexes = integer_list
                else: 
                    continue
            file.close()
    except FileNotFoundError:
        print(f"Error: The file '{banana_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    debug_json = {}
    instruction_data = {}
    try:
        with open(debug_path, 'r') as jfile:
            data = json.load(jfile)
            debug_json = data[binary_path]
            for src_code_line in debug_json.keys():
                if debug_json[src_code_line]:
                    instructions = debug_json[src_code_line]["instructions"]
                    for instruction in instructions:
                        byte_string = str(instruction["bytes"]).replace("[", "").replace("]", "").replace(",", "")
                        instruction_data[instruction["address"]] = {
                            "bytes": byte_string,
                            "asm": instruction["asm"],
                            "src": debug_json[src_code_line]["source"]
                        }
            jfile.close()
    except FileNotFoundError:
        print(f"Error: The file '{debug_path}' was not found.")
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{debug_path}'. Check for valid JSON format.")

    instructions_list_indexes = list(instruction_data.keys())

    print("Sussy Indexes")
    print(sussy_indexes)

    print("Starting Indexes of Instructions")
    print(instructions_list_indexes)

    critical_instruction_set = set()
    for sussy_index in sussy_indexes:
        critical_index = FindIndexImpacted(sussy_index, instructions_list_indexes)
        if critical_index == -1: # not in instructtion indexes?
            continue
        src_data = instruction_data[critical_index]["src"]
        if "assert" in src_data: # fault the assert statement itself
            continue
        else:
            critical_instruction_set.add(critical_index)
            print(f"{sussy_index} byte fault impacts the instruction @ {critical_index}")

    critical_instruction_indexes = list(critical_instruction_set)
    critical_instruction_indexes.sort()
    print(critical_instruction_indexes)
    out = ""

    for critical_index in critical_instruction_indexes:
        out = out + f"{critical_index}, {instruction_data[critical_index]["bytes"]}\n"

    print(out)

    out_file_path = os.path.join(out_path, f"critical-{name}.csv")

    with open(out_file_path, "w") as f:
        f.write(out)
        f.close()

    print(f"{out_file_path} created")

if __name__ == "__main__":
    main()

# python ../isolate.py ./Fault-Banana-x86-32-reset.txt ./m32.json ./m32.o x86-32-reset