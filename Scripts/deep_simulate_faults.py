import mmap
import os
import sys
import argparse
import subprocess
from tqdm import tqdm
import json
from Banana.bytes_binary import binary_to_byte_ints
from Banana.rewrite_binary import rewriteByteSection
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
        mutants = fault["mutants"]

        for mutant, offsets in mutants.items():
            mutant_bytes = binary_to_byte_ints(mutant)
            rewriteByteSection(byte_array, mutant_binary_path, int(index, 16), mutant_bytes)

            logger.info(f"mutant instruction @ {index} for bit offsets {offsets}")
            link_binary(architecture, mutant_binary_path, mutant_exec_path)
        
            mutant_result = run_binary(architecture, mutant_exec_path, time_out)
            if mutant_result["output"] != intended_result["output"]:
                mutant_result["incorrect"] = True

            out_result_path = os.path.join(out_folder, f"mutant-{index}-{mutant}.json")
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
    parser.add_argument("critical_mutants", default="./critical_mutants.json", type=str, help="Path to critical_mutants.json")
    parser.add_argument("out", default="./out", type=str, help="Path to output folder")
    parser.add_argument("architecture", default="None", type=str, help="Target Architecture")
    parser.add_argument("timeout", default=5, type=int, help="Max time for command")

    args = parser.parse_args()
    binary_path = args.binary
    critical_mutants_path = args.critical_mutants
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

    # Simulating Normal Operation
    original_exec_path = os.path.join(out_path, f"original.o")
    logger.info(original_exec_path)
    link_binary(architecture, binary_path, original_exec_path)
    intended_result = run_binary(architecture, original_exec_path, time_out)
  
    # Simulating Faults for Every Bit Offset
    temp_folder = os.path.join(out_path, "temporary")
    run(f"mkdir -p {temp_folder}")
    logger.info(temp_folder)
    critical_set_result_folder = os.path.join(out_path, "result", "critical_set")
    run(f"mkdir -p {critical_set_result_folder}")
    logger.info(critical_set_result_folder)
    critical_reset_result_folder = os.path.join(out_path, "result", "critical_reset")
    run(f"mkdir -p {critical_reset_result_folder}")
    logger.info(critical_reset_result_folder)
    critical_flip_result_folder = os.path.join(out_path, "result", "critical_flip")
    run(f"mkdir -p {critical_flip_result_folder}")
    logger.info(critical_flip_result_folder)

    mutant_binary_path = os.path.join(temp_folder, f"mutant.o")
    logger.info(mutant_binary_path)
    mutant_exec_path = os.path.join(temp_folder, f"mutexec.o")
    logger.info(mutant_exec_path)
    
    logger.info("Set fault critical mutants:")
    simulate_faults(critical_set_faults, byte_array, architecture, time_out, mutant_binary_path, mutant_exec_path, intended_result, critical_set_result_folder)
    logger.info("Rest fault critical mutants:")
    simulate_faults(critical_reset_faults, byte_array, architecture, time_out, mutant_binary_path, mutant_exec_path, intended_result, critical_reset_result_folder)
    logger.info("Flip fault critical mutants:")
    simulate_faults(critical_flip_faults, byte_array, architecture, time_out, mutant_binary_path, mutant_exec_path, intended_result, critical_flip_result_folder)


if __name__ == "__main__":
    main()