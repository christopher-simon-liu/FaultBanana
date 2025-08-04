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
import subprocess
import pandas as pd
from weasyprint import HTML
from Banana.print_logger import logger

def run(command):
    result = None
    try:
        result = subprocess.run([command], shell=True, check=True)
        logger.info("Command completed successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed with an error: {e}")
    return result

def show_fault(offset, binary_string):
    binary_list = list(binary_string)
    for i in range(8):
        position = offset + i
        binary_list[position] = "2"
    output = "".join(binary_list)
    return output

def generate_visual_data(critical_instruction, result_folder):
    data = {
        "index": 0,
        "chance": 0,
        "results": [],
        "unique_mutant_count": 0,
        "binary": "",
        "matrix": [],
        "crashes": 0,
        "timeouts": 0,
        "vulnerable": 0,
        "incorrect": 0,
        "correct": 0,
        "exit_code_counts": {},
        "sussy": [],
        "corrupt": [],
        "ticks": "0=correct\n1=crash\n2=timeout\n3=incorrect\n4=vulnerable\n5=zero\n6=one\n7=fault\n",
    }
    index = critical_instruction["index"]
    original = critical_instruction["original"]
    mutants = critical_instruction["mutants"]

    total_offsets = len(original) - 8 + 1
    data["binary"] = original
    data["results"] = [0] * total_offsets
    data["index"] = index
    pbar = tqdm(total=len(mutants))
    data["unique_mutant_count"] = len(mutants)

    for mutant, offsets in mutants.items():
        result_path = os.path.join(result_folder, f"mutant-{index}-{mutant}.json")
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
            for offset in offsets:
                data["results"][offset] = 1
            data["crashes"] += len(offsets)
                    
        elif result_json["vulnerable"]:
            # logic attack
            for offset in offsets:
                data["results"][offset] = 4
            data["vulnerable"] += len(offsets)
            data["sussy"].extend(offsets)

        elif result_json["timeout"]:
            # timeout
            for offset in offsets:
                data["results"][offset] = 2
            data["timeouts"] += len(offsets)

        elif result_json["incorrect"]:
            # corrupt
            for offset in offsets:
                data["results"][offset] = 3
            data["incorrect"] += len(offsets)
            data["corrupt"].extend(offsets)
        else:
            # pass
            for offset in offsets:
                data["results"][offset] = 0
            data["correct"] += len(offsets)
           
        pbar.update(1)
    pbar.close()

    visual_matrix = []

    for offset in range(total_offsets):
        result = data["results"][offset]
        binary_string = show_fault(offset, data["binary"])   
        visual_array = [int(n) + 5 for n in list(binary_string)]
        visual_array.append(result)
        arr = np.array(visual_array)
        if offset == 0:
            visual_matrix = arr
        else:
            visual_matrix = np.vstack((visual_matrix, arr))
    data["matrix"] = visual_matrix

    vulnerable_offsets = data["vulnerable"]
    attack_chance = round( vulnerable_offsets / total_offsets * 100, 2)
    logger.info(f"Attack success chance for instruction @ {index}: {attack_chance}%")
    data["chance"] = attack_chance

    return data

def create_banana(data, figure_name, out_path):
    matrix = data["matrix"]
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
    img = pyplot.imshow(matrix, interpolation='nearest', cmap=cmap, norm=norm)
   
    # make a color bar
    pyplot.colorbar(img, cmap=cmap, norm=norm, boundaries=bounds, ticks=[0,1,2,3,4,5,6,7,8])

    out_file_path = os.path.join(out_path, f"{figure_name}.png")
    fig.savefig(out_file_path)
    logger.info(f"{out_file_path} saved")
    pyplot.close()

def save_json(data, json_name, out_path):
    # matrix is not json serializable
    data.pop("matrix")
    out_file_path = os.path.join(out_path, f"{json_name}.json")
    with open(out_file_path, "w") as r:
        r.write(json.dumps(data, indent=1))
        r.close()
    logger.info(f"{out_file_path} created")

def list_files_by_extension(directory_path, extension):
    file_list = []
    for item in os.listdir(directory_path):
        full_path = os.path.join(directory_path, item)
        if os.path.isfile(full_path) and item.endswith(extension):
            file_list.append(full_path)
    return file_list

def get_index_chances(out_json_folder):
    output = {}
    vul_jsons = list_files_by_extension(out_json_folder, "json")
    for json_path in vul_jsons:
        try:
            with open(json_path, 'r') as j:
                critical = json.load(j)
                index = critical["index"]
                chance = critical["chance"]
                output[index] = chance
                j.close()
        except Exception as e:
            logger.error(f"An error occurred: {e}")
    return output

def create_tables(source_list, data_list):
    sf = pd.DataFrame(source_list, columns=["Source Code"])
    html_src = sf.to_html(index=False)
    html_data = ""
    if data_list:
        df = pd.DataFrame(data_list, columns=["Offset", "Bytecode", "Assembly Instruction", "Set Fault", "Reset Fault", "Flip Fault"])
        rounded_df = df.round(decimals=2)
        html_data = rounded_df.to_html(index=False)
    return html_src + html_data

def generate_pdf_report(debug_json, out_path):
    html_start = """
        <!DOCTYPE html>
        <html>
        <head>
        <style>
        table { border-collapse: collapse; width: 100%; }
        th, td { text-align: left; padding: 2px; }
        tr:nth-child(even){ background-color: #f2f2f2 }
        th { background-color: #36454F; color: white; }
        tr:hover {background-color: #fbe698;}
        </style>
        </head>
        <body>
    """
    html_end ="""
        </body>
        </html>
    """
    out_file_html = os.path.join(out_path, f"report.html")
    out_file_pdf = os.path.join(out_path, f"report.pdf")
    num_lines = len(debug_json.keys())
    pbar = tqdm(total=num_lines)

    with open(out_file_html, 'w') as f:
        f.write(html_start)
        for num in range(num_lines):
            if debug_json[str(num)] is None:
                pbar.update(1)
                continue
            else:
                block_json = debug_json[str(num)]
                s_table = [ 
                    [block_json["source"]], 
                ]
                d_table = [
                    [
                        instruction["address"],
                        instruction["code"],
                        instruction["asm"].replace("\t", "   "),
                        instruction["vulnerable"]["set"],
                        instruction["vulnerable"]["reset"],
                        instruction["vulnerable"]["flip"]
                        
                    ] for instruction in block_json["instructions"]
                ]
                to_write = create_tables(s_table, d_table)
                f.write(to_write)
                pbar.update(1)
        pbar.close()
        f.write(html_end)
        f.close()
    logger.info(f"{out_file_html} created")
    HTML(out_file_html).write_pdf(out_file_pdf)
    logger.info(f"{out_file_pdf} created")


def main():
    ## entry point of this program
    ## Parsing the arguments
    parser = argparse.ArgumentParser(description="Tool Options")
    parser.add_argument("critical_mutants", default="./critical_mutants.json", type=str, help="Path to critical_mutants.json")
    parser.add_argument("out", default="./out", type=str, help="Path to data folder")

    args = parser.parse_args()
    critical_mutants_path = args.critical_mutants
    out_path = args.out

    critical_mutants_json = {}
    try:
        with open(critical_mutants_path, 'r') as j:
            critical_mutants_json = json.load(j)
            j.close()
    except FileNotFoundError:
        logger.error(f"Error: The file '{critical_mutants_path}' was not found.")
    except json.JSONDecodeError:
        logger.error(f"Error: Could not decode JSON from '{critical_mutants_path}'. Check for valid JSON format.")

    offset = critical_mutants_json["offset"]
    size = critical_mutants_json["size"]

    critical_set_faults = critical_mutants_json["fault_models"]["set"]
    critical_reset_faults = critical_mutants_json["fault_models"]["reset"]
    critical_flip_faults = critical_mutants_json["fault_models"]["flip"]

    critical_set_result_folder = os.path.join(out_path, "result", "critical_set")
    critical_reset_result_folder = os.path.join(out_path, "result", "critical_reset")
    critical_flip_result_folder = os.path.join(out_path, "result", "critical_flip")

    critical_set_out_folder = os.path.join(out_path, "critical", "set")
    run(f"mkdir -p {critical_set_out_folder}")
    logger.info(critical_set_out_folder)
    critical_reset_out_folder = os.path.join(out_path, "critical", "reset")
    run(f"mkdir -p {critical_reset_out_folder}")
    logger.info(critical_reset_out_folder)
    critical_flip_out_folder = os.path.join(out_path, "critical", "flip")
    run(f"mkdir -p {critical_flip_out_folder}")
    logger.info(critical_flip_out_folder)

    unique_set_experiments = 0
    vul_set_experiments = 0
    if os.path.exists(critical_set_result_folder):
        for critical_instruction in critical_set_faults:
            index = critical_instruction["index"]
            critical_set_data = generate_visual_data(critical_instruction, critical_set_result_folder)
            create_banana(critical_set_data, f"critical-banana-set-{index}", critical_set_out_folder)
            save_json(critical_set_data, f"critical-banana-set-{index}", critical_set_out_folder)
            unique_set_experiments += critical_set_data["unique_mutant_count"]
            vul_set_experiments += critical_set_data["vulnerable"]
    else:
        logger.error("Result folder for set faults is missing")
    
    unique_reset_experiments = 0
    vul_reset_experiments = 0
    if os.path.exists(critical_reset_result_folder):
        for critical_instruction in critical_reset_faults:
            index = critical_instruction["index"]
            critical_reset_data = generate_visual_data(critical_instruction, critical_reset_result_folder)
            create_banana(critical_reset_data, f"critical-banana-reset-{index}", critical_reset_out_folder)
            save_json(critical_reset_data, f"critical-banana-reset-{index}", critical_reset_out_folder)
            unique_reset_experiments += critical_reset_data["unique_mutant_count"]
            vul_reset_experiments += critical_reset_data["vulnerable"]
    else:
        logger.error("Result folder for reset faults is missing")

    unique_flip_experiments = 0
    vul_flip_experiments = 0
    if os.path.exists(critical_flip_result_folder):
        for critical_instruction in critical_flip_faults:
            index = critical_instruction["index"]
            critical_flip_data = generate_visual_data(critical_instruction, critical_flip_result_folder)
            create_banana(critical_flip_data, f"critical-banana-flip-{index}", critical_flip_out_folder)
            save_json(critical_flip_data, f"critical-banana-flip-{index}", critical_flip_out_folder)
            unique_flip_experiments += critical_flip_data["unique_mutant_count"]
            vul_flip_experiments += critical_flip_data["vulnerable"]
    else:
        logger.error("Result folder for flip faults is missing")

    # generate report
    debug_json_path = os.path.join(out_path, f"debug.json")
    debug_json = {}
    try:
        with open(debug_json_path, 'r') as j:
            debug_json = json.load(j)
            j.close()
    except FileNotFoundError:
        logger.error(f"Error: The file '{debug_json_path}' was not found.")
    except json.JSONDecodeError:
        logger.error(f"Error: Could not decode JSON from '{debug_json_path}'. Check for valid JSON format.")

    vulnerabilities = {
        "set": {},
        "reset": {},
        "flip": {}
    }
    vulnerabilities["set"] = get_index_chances(critical_set_out_folder)
    vulnerabilities["reset"] = get_index_chances(critical_reset_out_folder)
    vulnerabilities["flip"] = get_index_chances(critical_flip_out_folder)
    
    instruction_count = 0

    for src_code_line in debug_json.keys():
        if debug_json[src_code_line]:
            instructions = debug_json[src_code_line]["instructions"]
            for instruction in instructions:
                instruction_count += 1
                index = instruction["address"]
                instruction["vulnerable"] = {
                    "set": 0,
                    "reset": 0,
                    "flip": 0
                } 
                if index in vulnerabilities["set"]:
                    instruction["vulnerable"]["set"] = vulnerabilities["set"][index]
                if index in vulnerabilities["reset"]:
                    instruction["vulnerable"]["reset"] = vulnerabilities["reset"][index]
                if index in vulnerabilities["flip"]:
                    instruction["vulnerable"]["flip"] = vulnerabilities["flip"][index]

    out_report_path = os.path.join(out_path, f"report.json")
    with open(out_report_path, "w") as r:
        r.write(json.dumps(debug_json, indent=1))
        r.close()
    logger.info(f"{out_report_path} created")

    generate_pdf_report(debug_json, out_path)

    critical_set_count = 0
    for index, chance in vulnerabilities["set"].items():
        if chance > 0:
            critical_set_count += 1
    critical_reset_count = 0
    for index, chance in vulnerabilities["reset"].items():
        if chance > 0:
            critical_reset_count += 1
    critical_flip_count = 0
    for index, chance in vulnerabilities["flip"].items():
        if chance > 0:
            critical_flip_count += 1

    logger.info(f"Total Instructions: {instruction_count}")
    logger.info(f"Experiments: {unique_set_experiments}")
    logger.info(f"Vulnerable to Set Fault: {vul_set_experiments}")
    logger.info(f"Total Set Fault Instructions: {critical_set_count}")
    logger.info(f"Experiments: {unique_reset_experiments}")
    logger.info(f"Vulnerable to Reset Fault: {vul_reset_experiments}")
    logger.info(f"Toal Reset Fault Instructions: {critical_reset_count}")
    logger.info(f"Experiments: {unique_flip_experiments}")
    logger.info(f"Vulnerable to Flip Fault: {vul_flip_experiments}")
    logger.info(f"TOtal Flip Fault Instructions: {critical_flip_count}")

if __name__ == "__main__":
    main()
