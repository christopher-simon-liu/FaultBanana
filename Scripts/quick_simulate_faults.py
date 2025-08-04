import mmap
import os
import sys
import argparse
import subprocess
from tqdm import tqdm
import json
from Banana.rewrite_binary import rewriteByte
from Banana.link_binary import link_binary
from Banana.run_binary import run_binary
from Banana.print_logger import logger

def run(command):
    result = None
    try:
        result = subprocess.run([command], shell=True, check=True)
        logger.info("Command completed successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed with an error: {e}")
    return result

def simulate_faults(fault_list, byte_array, architecture, time_out, mutant_binary_path, mutant_exec_path, intended_result, out_folder):
    pbar = tqdm(total=len(fault_list))
    for fault in fault_list:
        index = fault["index"]
        original = fault["original"]
        mutant = fault["mutant"]

        rewriteByte(byte_array, mutant_binary_path, int(index, 16), mutant)
        logger.info(f"mutant @ {index}")
        link_binary(architecture, mutant_binary_path, mutant_exec_path)
        
        mutant_result = run_binary(architecture, mutant_exec_path, time_out)
        if mutant_result["output"] != intended_result["output"]:
            mutant_result["incorrect"] = True

        out_result_path = os.path.join(out_folder, f"mutant-{index}.json")
        with open(out_result_path, "w") as r:
            r.write(json.dumps(mutant_result, indent=1))
            r.close()

        logger.info(f"{out_result_path} created")

        pbar.update(1)
    pbar.close()

def main():  
    ## entry point of this program
    ## Parsing the arguments
    parser = argparse.ArgumentParser(description="Tool Options")
    parser.add_argument("binary", default="./binary.o", type=str, help="Path to binary.o")
    parser.add_argument("mutants", default="./mutants.json", type=str, help="Path to mutants.json")
    parser.add_argument("out", default="./out", type=str, help="Path to output folder")
    parser.add_argument("architecture", default="None", type=str, help="Target Architecture")
    parser.add_argument("timeout", default=5, type=int, help="Max time for command")

    args = parser.parse_args()
    binary_path = args.binary
    mutants_path = args.mutants
    out_path = args.out
    architecture = args.architecture
    time_out = args.timeout

    byte_array=[]
    try:
        with open(binary_path, "r+b") as f:
            mm = mmap.mmap(f.fileno(), 0)
            byte_array = bytearray(mm)
            sizefile=len(byte_array)
            logger.info(f"{sizefile} bytes in binary")
            f.close()
    except FileNotFoundError:
        logger.error(f"Error: The file '{binary_path}' was not found.")

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

    # Simulating Normal Operation
    original_exec_path = os.path.join(out_path, f"original.o")
    logger.info(original_exec_path)
    link_binary(architecture, binary_path, original_exec_path)
    intended_result = run_binary(architecture, original_exec_path, time_out)
  
    # Simulating Faults for Every Byte Offset
    temp_folder = os.path.join(out_path, "temporary")
    run(f"mkdir -p {temp_folder}")
    logger.info(temp_folder)
    set_result_folder = os.path.join(out_path, "result", "set")
    run(f"mkdir -p {set_result_folder}")
    logger.info(set_result_folder)
    reset_result_folder = os.path.join(out_path, "result", "reset")
    run(f"mkdir -p {reset_result_folder}")
    logger.info(reset_result_folder)
    flip_result_folder = os.path.join(out_path, "result", "flip")
    run(f"mkdir -p {flip_result_folder}")
    logger.info(flip_result_folder)

    mutant_binary_path = os.path.join(temp_folder, f"mutant.o")
    logger.info(mutant_binary_path)
    mutant_exec_path = os.path.join(temp_folder, f"mutexec.o")
    logger.info(mutant_exec_path)
    
    logger.info("Set fault mutants:")
    simulate_faults(set_faults, byte_array, architecture, time_out, mutant_binary_path, mutant_exec_path, intended_result, set_result_folder)
    logger.info("Reset fault mutants:")
    simulate_faults(reset_faults, byte_array, architecture, time_out, mutant_binary_path, mutant_exec_path, intended_result, reset_result_folder)
    logger.info("Flip fault mutants:")
    simulate_faults(flip_faults, byte_array, architecture, time_out, mutant_binary_path, mutant_exec_path, intended_result, flip_result_folder)


if __name__ == "__main__":
    main()