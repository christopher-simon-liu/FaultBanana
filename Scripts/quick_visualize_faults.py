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
from Banana.print_logger import logger

def generate_visual_data(fault_list, offset, size, result_folder):
    data = {
        "array": [0] * size,
        "crashes": 0,
        "timeouts": 0,
        "vulnerable": 0,
        "incorrect": 0,
        "correct": 0,
        "exit_code_counts": {},
        "sussy": [],
        "corrupt": [],
        "ticks": "0=correct\n1=crash\n2=timeout\n3=incorrect\n4=vulnerable\n5=placeholder\n"
    }
    pbar = tqdm(total=len(fault_list))
    for fault in fault_list:
        index = fault["index"]
        original = fault["original"]
        mutant = fault["mutant"]

        result_path = os.path.join(result_folder, f"mutant-{index}.json")
        position = int(index, 16) - offset

        result_json = {}
        try:
            with open(result_path, 'r') as j:
                result_json = json.load(j)
                j.close()
        except FileNotFoundError:
            logger.error(f"Error: The file '{result_path}' was not found.")
        except json.JSONDecodeError:
            logger.error(f"Error: Could not decode JSON from '{result_path}'. Check for valid JSON format.")
            
        exit_code = result_json["exit"]
        if exit_code in data["exit_code_counts"].keys():
            data["exit_code_counts"][exit_code] += 1
        else:
            data["exit_code_counts"][exit_code] = 1

        if not "None" in result_json["error"] and not "assert" in result_json["error"].lower():
            # crash 
            data["array"][position] = 1
            data["crashes"] += 1
                    
        elif result_json["vulnerable"]:
            # logic attack
            data["array"][position] = 4
            data["vulnerable"] += 1
            data["sussy"].append(index)

        elif result_json["timeout"]:
            # timeout
            data["array"][position] = 2
            data["timeouts"] += 1

        elif result_json["incorrect"]:
            # corrupt
            data["array"][position] = 3                
            data["incorrect"] += 1
            data["corrupt"].append(index)

        else:
            # pass
            data["array"][position] = 0
            data["correct"] += 1
           
        pbar.update(1)
    pbar.close()
    return data

def create_banana(data, figure_name, out_path, size):
    visual_array = data["array"]
    # Calculate the square root
    sqrt_result = math.sqrt(size)
    # Round the square root up to the nearest integer
    rounded_up_result = math.ceil(sqrt_result)
    # big square
    rowlength = rounded_up_result
    collength = rounded_up_result
    fill = rowlength * collength - size
    visual_array.extend([5]*fill)
    
    arr = np.array(visual_array)
    matrix = arr.reshape(rowlength, collength)
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
    logger.info(f"{out_file_path} saved")
    pyplot.close()

def save_json(data, json_name, out_path):
    out_file_path = os.path.join(out_path, f"{json_name}.json")
    with open(out_file_path, "w") as r:
        r.write(json.dumps(data, indent=1))
        r.close()
    logger.info(f"{out_file_path} created")

def main():
    ## entry point of this program
    ## Parsing the arguments
    parser = argparse.ArgumentParser(description="Tool Options")
    parser.add_argument("mutants", default="./mutants.json", type=str, help="Path to mutants.json")
    parser.add_argument("out", default="./out", type=str, help="Path to data folder")

    args = parser.parse_args()
    mutants_path = args.mutants
    out_path = args.out

    mutants_json = {}
    try:
        with open(mutants_path, 'r') as j:
            mutants_json = json.load(j)
            j.close()
    except FileNotFoundError:
        logger.error(f"Error: The file '{mutants_path}' was not found.")
    except json.JSONDecodeError:
        logger.error(f"Error: Could not decode JSON from '{mutants_path}'. Check for valid JSON format.")

    offset = mutants_json["offset"]
    size = mutants_json["size"]

    set_faults = mutants_json["fault_models"]["set"]
    reset_faults = mutants_json["fault_models"]["reset"]
    flip_faults = mutants_json["fault_models"]["flip"]

    set_result_folder = os.path.join(out_path, "result", "set")
    reset_result_folder = os.path.join(out_path, "result", "reset")
    flip_result_folder = os.path.join(out_path, "result", "flip")

    set_data = {}
    if os.path.exists(set_result_folder):
        set_data = generate_visual_data(set_faults, offset, size, set_result_folder)
        create_banana(set_data, f"banana-set", out_path, size)
        save_json(set_data, f"banana-set", out_path)
    else:
        logger.error("Result folder for set faults is missing")
    
    reset_data = {}
    if os.path.exists(reset_result_folder):
        reset_data = generate_visual_data(reset_faults, offset, size, reset_result_folder)
        create_banana(reset_data, f"banana-reset", out_path, size)
        save_json(reset_data, f"banana-reset", out_path)
    else:
        logger.error("Result folder for reset faults is missing")

    flip_data = {}
    if os.path.exists(flip_result_folder):
        flip_data = generate_visual_data(flip_faults, offset, size, flip_result_folder)
        create_banana(flip_data, f"banana-flip", out_path, size)
        save_json(flip_data, f"banana-flip", out_path)
    else:
        logger.error("Result folder for flip faults is missing")

    logger.info(f"Experiments: {len(set_faults)}")
    logger.info(f"Vulnerable to Set Fault: {set_data["vulnerable"]}")
    logger.info(f"Experiments: {len(reset_faults)}")
    logger.info(f"Vulnerable to Reset Fault: {reset_data["vulnerable"]}")
    logger.info(f"Experiments: {len(flip_faults)}")
    logger.info(f"Vulnerable to Flip Fault: {flip_data["vulnerable"]}")

if __name__ == "__main__":
    main()
