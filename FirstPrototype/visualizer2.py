import os
from PIL import Image
import sys
import argparse
import matplotlib as mpl
from matplotlib import pyplot
import numpy as np
import math
from tqdm import tqdm
import json

def list_files_in_dir(dir_path):
    files = []
    for item in os.listdir(dir_path):
        item_path = os.path.join(dir_path, item)
        if os.path.isfile(item_path):
            files.append(item_path)
    return files

def parseDebugJSON(binary_path, debug_path):
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
                        instruction_data[instruction["address"]] = {
                            "bytes": instruction["bytes"],
                            "asm": instruction["asm"],
                            "src": debug_json[src_code_line]["source"]
                        }
    except FileNotFoundError:
        print(f"Error: The file '{debug_path}' was not found.")
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{debug_path}'. Check for valid JSON format.")
    return instruction_data

def showFault(offset, binary_string):
    binary_list = list(binary_string)
    for i in range(8):
        position = offset + i
        binary_list[position] = "2"
    output = "".join(binary_list)
    return output

def parseSnippetsJSON(snippets_path):
    snippets_json = {}
    try:
        with open(snippets_path, 'r') as jfile:
            data = json.load(jfile)
            for instruction_index in data.keys():
                mutants = data[instruction_index]["mutants"]
                for byte_string, offsets_string in mutants.items():
                    offsets_list = offsets_string.split()
                    bytes_list = byte_string.split()
                    for offset in offsets_list:
                        new_key = f"{instruction_index}-{offset}"
                        # each byte is 8 bits
                        binary_list = [bin(int(i))[2:].zfill(8) for i in bytes_list]
                        binary_string = "".join(binary_list)
                        snippets_json[new_key] = showFault(int(offset), binary_string)
    except FileNotFoundError:
        print(f"Error: The file '{snippets_path}' was not found.")
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{snippets_path}'. Check for valid JSON format.")
    
    return snippets_json

def main():
    ## entry point of this program
    ## Parsing the arguments
    parser = argparse.ArgumentParser(description="Tool Options")
    parser.add_argument("outputs", default="./critical_outputs", type=str, help="Path to folder with output.txt files")
    parser.add_argument("mutants", default="./critical_mutants", type=str, help="Path to folder with mutant.o files")
    parser.add_argument("name", default="Fault Banana", type=str, help="Name for figure")
    parser.add_argument("out", default="./out", type=str, help="Path to output folder")
    parser.add_argument("debug", default="./m32.json", type=str, help="Path to json file with assembly debugging info")
    parser.add_argument("binary", default="./m32.o", type=str, help="Path to binary.o")
    parser.add_argument("snippets", default="./snippets.json", type=str, help="Path to instruction snippets.json")

    args = parser.parse_args()
    outputs_path = args.outputs
    mutants_path = args.mutants
    figure_name = args.name
    out_path = args.out
    debug_path = args.debug
    binary_path = args.binary
    snippets_path = args.snippets

    mutants = list_files_in_dir(mutants_path)
    results = {}
    pbar = tqdm(total=len(mutants))

    outputs = list_files_in_dir(outputs_path)

    instruction_data = parseDebugJSON(binary_path, debug_path)
    snippets_json = parseSnippetsJSON(snippets_path)
    # print(instruction_data)
    
    for file in outputs:
        file_name = os.path.basename(file)
        temp = file_name
        binary_name = temp[:temp.index('-')]
        temp = temp[temp.index('-')+1:]
        instruction_num = temp[:temp.index('-')]
        temp = temp[temp.index('-')+1:]
        fault_model = temp[:temp.index('-')]
        temp = temp[temp.index('-')+1:]
        offsets = [int(s) for s in temp[:temp.index('.o.txt')].split("_")]

        if instruction_num not in results.keys():
            results[instruction_num] = {
                "outputs": {},
                "crashes": 0,
                "timeouts": 0,
                "vulnerable": 0,
                "incorrect": 0,
                "correct": 0,
                "exit_code_counts": {},
                "err_message_counts": {},
                "sussy": [],
                "corrupt": []
            }
    
        with open(file, "r") as f:
            outputs = results[instruction_num]["outputs"]
            count = len(offsets)
            lines = f.readlines()

            err_line = lines[2]
            return_line = lines[3]
            timeout_line = lines[4]
            incorrect_line = lines[5]
            vulnerable_line = lines[6]

            exit_code_counts = results[instruction_num]["exit_code_counts"] 
            exit_code = return_line[return_line.index(":")+1:].strip()
            if exit_code in exit_code_counts.keys():
                exit_code_counts[exit_code] += 1
            else:
                exit_code_counts[exit_code] = 1

            if not "None" in err_line and not "assert" in err_line.lower():
                # crash 
                for bit_offset in offsets:
                    outputs[bit_offset] = 1
                results[instruction_num]["crashes"] += count

                err_message_counts = results[instruction_num]["err_message_counts"]
                err_message = err_line[err_line.index(":")+1:].strip()
                if err_message in err_message_counts.keys():
                    err_message_counts[err_message] += 1
                else:
                    err_message_counts[err_message] = 1              
            
            elif "True" in vulnerable_line:
                # logic attack
                for bit_offset in offsets:
                    outputs[bit_offset] = 4
                results[instruction_num]["vulnerable"] += count

                results[instruction_num]["sussy"].extend(offsets)

            elif "True" in timeout_line:
                # infinite loop
                for bit_offset in offsets:
                    outputs[bit_offset] = 2
                results[instruction_num]["timeouts"] += count

            elif "True" in incorrect_line: 
                # corrupt output
                for bit_offset in offsets:
                    outputs[bit_offset] = 3
                results[instruction_num]["incorrect"] += count  

                results[instruction_num]["corrupt"].extend(offsets)
                
            else:
                # correct output
                for bit_offset in offsets:
                    outputs[bit_offset] = 0

                results[instruction_num]["correct"] += count
            f.close()
        pbar.update(1)
    pbar.close()

    for instruction_num in results.keys():

        outputs = results[instruction_num]["outputs"]
        size = len(outputs.keys())
        results_array = [0] * size
        for i in range(size):
            results_array[i] = outputs[i]

        crash_count = results[instruction_num]["crashes"]
        timeout_count = results[instruction_num]["timeouts"]
        vulnerable_count = results[instruction_num]["vulnerable"]
        incorrect_count = results[instruction_num]["incorrect"]
        correct_count = results[instruction_num]["correct"]
        exit_code_counts = results[instruction_num]["exit_code_counts"]
        err_message_counts = results[instruction_num]["err_message_counts"]
        sussy_list = results[instruction_num]["sussy"]
        corrupt_list = results[instruction_num]["corrupt"]

        address = int(instruction_num)
        bytes_data = instruction_data[address]["bytes"]
        asm_data = instruction_data[address]["asm"]
        src_data = instruction_data[address]["src"]

        print(f"Critical Instruction {instruction_num} \n")
        print(f"Instruction bytes: {str(bytes_data)}\n")
        print(f"Instruction assembly: {str(asm_data)}\n")
        print(f"Source code: {str(src_data)}\n")

        print(f"Sussy: {sorted(sussy_list)}\n")
        print(f"Corrupt: {sorted(corrupt_list)}\n")

        attacks = len(sussy_list)
    
        print(f"Total Byte Mutations: {size}\n")
        print(f"Total Correct Mutations: {correct_count}\n")
        print(f"Total Crashing Mutations: {crash_count}\n")
        print(f"Total Timeout Mutations: {timeout_count}\n")
        print(f"Total Incorrect Mutations: {incorrect_count}\n")
        print(f"Total Vulnerable Mutations: {vulnerable_count}\n")
    
        print(f"Exit Codes: {str(exit_code_counts)}\n")
        print(f"Error Messages: {str(err_message_counts)}\n")

        attack_chance = round(attacks / size * 100, 2)
        print(f"Attack success chance: {attack_chance}%")

        # offset translation square

        visual_matrix = []

        for offset in range(size):
            result = results_array[offset]
            key = f"{instruction_num}-{offset}" 
            binary_string = snippets_json[key]
            visual_array = [int(n) + 5 for n in list(binary_string)]
            visual_array.append(result)
            arr = np.array(visual_array)

            if offset == 0:
                visual_matrix = arr
            else:
                visual_matrix = np.vstack((visual_matrix, arr))
    
        ticks = """
        0 = correct\n
        1 = crash\n
        2 = timeout\n
        3 = incorrect\n
        4 = vulnerable\n
        5 = zero \n
        6 = one \n
        7 = fault \n
        """
        print(ticks)
        print(str(visual_matrix))

        # Colors
        BLUE_GREEN = "#15b5b0"
        CYAN = "#6dece0"
        CHAMPAGNE = "#fbe698"
        HOT_PINK = "#FF69BF"
        PURPLE = "#A020F0"
        CHARCOAL = "#36454F"
        WHITISH = "#fafafa"
        GREYISH = "#808080"


        fig = pyplot.figure(figure_name)

        cmap = mpl.colors.ListedColormap([CHAMPAGNE, CYAN, BLUE_GREEN, HOT_PINK, PURPLE, CHARCOAL, WHITISH, GREYISH])
        bounds=[0,1,2,3,4,5,6,7,8]
        norm = mpl.colors.BoundaryNorm(bounds, cmap.N)

        # tell imshow about color map so that only set colors are used
        img = pyplot.imshow(visual_matrix, interpolation='nearest', cmap=cmap, norm=norm)
   
        # make a color bar
        # pyplot.colorbar(img, cmap=cmap, norm=norm, boundaries=bounds, ticks=[0,1,2,3,4,5,6])

        out_file_path = os.path.join(out_path, f"{figure_name}-i{instruction_num}-{attack_chance}%.png")
        fig.savefig(out_file_path)
        
        print(f"{out_file_path} saved")

        print("*"*42)
   

if __name__ == "__main__":
    main()
