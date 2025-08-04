# Required imports
import mmap
import os
import argparse
import json
from Banana.fault_model import fault_set_byte_hex, fault_reset_byte_hex, fault_flip_byte_hex
from Banana.print_logger import logger

def main():  
    ## entry point of this program
    ## Parsing the arguments
    parser = argparse.ArgumentParser(description="Tool Options")
    parser.add_argument("binary", default="./binary.o", type=str, help="Path to binary.o")
    parser.add_argument("offset", default=0, type=int, help="Starting byte index")
    parser.add_argument("size", default=100, type=int, help="Range of bytes of interest, e.g. size of .text")
    parser.add_argument("out", default="./out", type=str, help="Path to output folder")

    args = parser.parse_args()
    binary_path = args.binary
    offset = args.offset
    size = args.size
    out_path = args.out

    byte_array=[]
    
    with open(binary_path, "r+b") as f:
      mm = mmap.mmap(f.fileno(), 0)
      byte_array = bytearray(mm)
      sizefile=len(byte_array)
      logger.info(f"{sizefile} bytes in binary")
      f.close()

    mutant_data = {
        "offset": offset,
        "size": size,
        "fault_models": {
            "set": [],
            "reset": [],
            "flip": []
        }
    }
    for i in range(size):
        # offset is added to addresses
        position = offset + i
        original = byte_array[int(position)]
        set_mutant = fault_set_byte_hex(original)
        reset_mutant = fault_reset_byte_hex(original)
        flip_mutant = fault_flip_byte_hex(original)
        mutant_data["fault_models"]["set"].append({
            "index": hex(position),
            "original": original,
            "mutant": set_mutant
        })
        mutant_data["fault_models"]["reset"].append({
            "index": hex(position),
            "original": original,
            "mutant": reset_mutant
        })
        mutant_data["fault_models"]["flip"].append({
            "index": hex(position),
            "original": original,
            "mutant": flip_mutant
        })

    out_file_path = os.path.join(out_path, f"mutants.json")
    with open(out_file_path, "w") as f:
        f.write(json.dumps(mutant_data, indent=1))
        f.close()
    logger.info(f"{out_file_path} created")


if __name__ == "__main__":
    main()