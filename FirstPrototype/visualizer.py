import os
from PIL import Image
import sys
import argparse
import matplotlib as mpl
from matplotlib import pyplot
import numpy as np
import math
from tqdm import tqdm

def list_files_in_dir(dir_path):
    files = []
    for item in os.listdir(dir_path):
        item_path = os.path.join(dir_path, item)
        if os.path.isfile(item_path):
            files.append(item_path)
    return files


def main():
    ## entry point of this program
    ## Parsing the arguments
    parser = argparse.ArgumentParser(description="Tool Options")
    parser.add_argument("outputs", default="./outputs", type=str, help="Path to folder with output.txt files")
    parser.add_argument("mutants", default="./mutants", type=str, help="Path to folder with mutant.o files")
    parser.add_argument("name", default="Fault Banana", type=str, help="Name for figure")
    parser.add_argument("--o", default="./", type=str, help="Path to output folder")

    args = parser.parse_args()
    outputs_path = args.outputs
    mutants_path = args.mutants
    figure_name = args.name
    out_path = args.o

    mutants = list_files_in_dir(mutants_path)
    result = [0] * len(mutants)
    pbar = tqdm(total=len(mutants))

    outputs = list_files_in_dir(outputs_path)
    crashes = 0
    timeouts = 0
    vulnerable = 0
    incorrect = 0
    correct = 0
    exit_code_counts = {}
    err_message_counts = {}
    sussy = []
    corrupt = []

    for file in outputs:
        name = os.path.basename(file)
        index = int(name[name.index('-')+1:name.index(".o.txt")])
        with open(file, "r") as f:
            lines = f.readlines()

            err_line = lines[2]
            return_line = lines[3]
            timeout_line = lines[4]
            incorrect_line = lines[5]
            vulnerable_line = lines[6]
            
            exit_code = return_line[return_line.index(":")+1:].strip()
            if exit_code in exit_code_counts.keys():
                exit_code_counts[exit_code] += 1
            else:
                exit_code_counts[exit_code] = 1
            
            if not "None" in err_line and not "assert" in err_line.lower():
                # crash 
                result[index] = 1
                crashes += 1
             
                err_message = err_line[err_line.index(":")+1:].strip()
                if err_message in err_message_counts.keys():
                    err_message_counts[err_message] += 1
                else:
                    err_message_counts[err_message] = 1
                    
            elif "True" in vulnerable_line:
                # logic attack
                result[index] = 4
                vulnerable += 1
                sussy.append(index)

            elif "True" in timeout_line:
                # timeout
                result[index] = 2
                timeouts += 1

            elif "True" in incorrect_line:
                # corrupt output
                result[index] = 3
                incorrect += 1
                corrupt.append(index)


            else:
                # correct output
                result[index] = 0
                correct += 1
            f.close()
                
        pbar.update(1)
    pbar.close()

    print(f"Sussy: {str(sorted(sussy))}\n")
    print(f"Corrupt: {str(sorted(corrupt))}\n")
    size = len(result)
    
    print(f"Total Byte Mutations: {size}\n")
    print(f"Total Correct Mutations: {correct}\n")
    print(f"Total Crashing Mutations: {crashes}\n")
    print(f"Total Timeout Mutations: {timeouts}\n")
    print(f"Total Incorrect Mutations: {incorrect}\n")
    print(f"Total Vulnerable Mutations: {vulnerable}\n")

    print(f"Exit Codes: {str(exit_code_counts)}\n")
    print(f"Error Messages: {str(err_message_counts)}\n")

    # Calculate the square root
    sqrt_result = math.sqrt(size)
    # Round the square root up to the nearest integer
    rounded_up_result = math.ceil(sqrt_result)

    # big square?
    rowlength = rounded_up_result
    collength = rounded_up_result

    fill = rowlength * collength - size
    result.extend([5]*fill)
    # print(result)
    arr = np.array(result)
    matrix = arr.reshape(rowlength, collength)
    ticks = """
    0 = correct\n
    1 = crash\n
    2 = timeout\n
    3 = incorrect\n
    4 = vulnerable\n
    5 = placeholder\n
    """
    print(ticks)
    print(str(matrix))

    # Colors
    BLUE_GREEN = "#15b5b0"
    CYAN = "#6dece0"
    CHAMPAGNE = "#fbe698"
    CHARCOAL = "#36454F"
    HOT_PINK = "#FF69BF"
    PURPLE = "#A020F0"

    fig = pyplot.figure(figure_name)

    cmap = mpl.colors.ListedColormap([CHAMPAGNE, CYAN, BLUE_GREEN, HOT_PINK, PURPLE, CHARCOAL])
    bounds=[0,1,2,3,4,5,6]
    norm = mpl.colors.BoundaryNorm(bounds, cmap.N)

    # tell imshow about color map so that only set colors are used
    img = pyplot.imshow(matrix, interpolation='nearest', cmap=cmap, norm=norm)
   
    # make a color bar
    pyplot.colorbar(img, cmap=cmap, norm=norm, boundaries=bounds, ticks=[0,1,2,3,4,5,6])

    out_file_path = os.path.join(out_path, f"{figure_name}.png")
    fig.savefig(out_file_path)
    print(f"{out_file_path} saved")

if __name__ == "__main__":
    main()
