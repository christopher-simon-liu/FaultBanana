# Required imports
import mmap
import os
import argparse
import json
from Banana.fault_model import fault_set_byte_binary_string, fault_reset_byte_binary_string, fault_flip_byte_binary_string
from Banana.disassemble_binary import disassemble_binary, parse_disassembly
from Banana.isolate_critical import isolate_critical
from Banana.bytes_binary import binary_to_byte_ints, byte_ints_to_binary
from Banana.print_logger import logger

def generate_mutants(critical_instructions, fault_model):
    mutant_data = []
    for address, byte_int_list in critical_instructions.items():
        big_binary = byte_ints_to_binary(byte_int_list)
        total_offsets = len(big_binary) - 8 + 1
        logger.info(f"Possible offsets: {total_offsets}")
        mutants = {}
        for offset in range(total_offsets):
            mutant_binary = ""
            if fault_model == "set":
                mutant_binary = fault_set_byte_binary_string(offset, big_binary)
            elif fault_model == "reset":
                mutant_binary = fault_reset_byte_binary_string(offset, big_binary)
            elif fault_model == "flip":
                mutant_binary = fault_flip_byte_binary_string(offset, big_binary)
            else:
                logger.warn("invalid fault model")

            mutant_byte_ints = binary_to_byte_ints(mutant_binary)
                
            # group identical binary
            if mutant_binary in mutants.keys():
                mutants[mutant_binary].append(offset)
            else:
                mutants[mutant_binary] = []
                mutants[mutant_binary].append(offset)
        logger.info(big_binary)
        mutant_data.append({   
            "index": address,
            "original": big_binary,
            "mutants": mutants
        })
    return mutant_data
def main():  
    ## entry point of this program
    ## Parsing the arguments
    parser = argparse.ArgumentParser(description="Tool Options")
    parser.add_argument("binary", default="./binary.o", type=str, help="Path to binary.o")
    parser.add_argument("offset", default=0, type=int, help="Starting byte index")
    parser.add_argument("size", default=100, type=int, help="Range of bytes of interest, e.g. size of .text")
    parser.add_argument("out", default="./out", type=str, help="Path to output folder")
    parser.add_argument("architecture", default="None", type=str, help="Target Architecture")

    args = parser.parse_args()
    binary_path = args.binary
    offset = args.offset
    size = args.size
    out_path = args.out
    architecture = args.architecture

    byte_array=[]
    
    with open(binary_path, "r+b") as f:
      mm = mmap.mmap(f.fileno(), 0)
      byte_array = bytearray(mm)
      sizefile=len(byte_array)
      logger.info(f"{sizefile} bytes in binary")
      f.close()
    
    # disassemble
    out_debug_asm = os.path.join(out_path, f"debug.asm")
    disassemble_binary(architecture, binary_path, out_debug_asm)
    logger.info(f"{out_debug_asm} created")

    out_debug_json = os.path.join(out_path, f"debug.json")
    # offset is added to addresses
    debug_data = parse_disassembly(out_debug_asm, byte_array, offset, architecture)
    with open(out_debug_json, "w") as f:
        f.write(json.dumps(debug_data, indent=1))
        f.close()
    logger.info(f"{out_debug_json} created")

    # isolate critical
    out_banana_set = os.path.join(out_path, f"banana-set.json")
    out_banana_reset = os.path.join(out_path, f"banana-reset.json")
    out_banana_flip = os.path.join(out_path, f"banana-flip.json")
    
    critical_data = {
        "fault_models": {
            "set": {},
            "reset": {},
            "flip": {}
        }
    }
    if os.path.exists(out_banana_set):
        critical_set = isolate_critical(out_banana_set, out_debug_json)
        critical_data["fault_models"]["set"] = critical_set
    else:
        logger.error("Quick Analysis banana-set.json is missing")

    if os.path.exists(out_banana_reset):
        critical_reset = isolate_critical(out_banana_reset, out_debug_json)
        critical_data["fault_models"]["reset"] = critical_reset
    else:
        logger.error("Quick Analysis banana-reset.json is missing")

    if os.path.exists(out_banana_flip):
        critical_flip = isolate_critical(out_banana_flip, out_debug_json)
        critical_data["fault_models"]["flip"] = critical_flip
    else:
        logger.error("Quick Analysis banana-flip.json is missing")

    
    # generate critical mutants
    critical_mutant_data = {
        "offset": offset,
        "size": size,
        "fault_models": {
            "set": [],
            "reset": [],
            "flip": []
        }
    }

    critical_set = critical_data["fault_models"]["set"] 
    if critical_set:
        critical_mutant_data["fault_models"]["set"] = generate_mutants(critical_set, "set")
    
    critical_reset = critical_data["fault_models"]["reset"] 
    if critical_reset:
        critical_mutant_data["fault_models"]["reset"] = generate_mutants(critical_reset, "reset")

    critical_flip = critical_data["fault_models"]["flip"]
    if critical_flip: 
        critical_mutant_data["fault_models"]["flip"] = generate_mutants(critical_set, "flip")

    out_file_path = os.path.join(out_path, f"critical_mutants.json")
    with open(out_file_path, "w") as f:
        f.write(json.dumps(critical_mutant_data, indent=1))
        f.close()
    logger.info(f"{out_file_path} created")

if __name__ == "__main__":
    main()