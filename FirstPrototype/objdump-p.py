import os
import sys
import argparse
import subprocess
import re
import json
import mmap

from architectures import architectures_supported

def OriginalOverwrite(values, position, length_bytes):
    original = []
    for i in range(length_bytes):
        index = position + i
        original.append(values[index])
    return original

def parse_objdump(file_path, byte_array, offset, target):
    result = {}
    name_found = False
    file_name = ""
    line_number = 0
    current = None

    regex_string = architectures_supported[target]["parse_regex"]
    
    with open(file_path) as f:
        
        for line in f:
            # instruction info regex
            m = re.match(regex_string, line.strip())
            if not name_found and "file format" in line:
                file_name = line[0:line.rindex(":")]
                name_found = True
                # print(file_name)
            elif len(line.strip()) == 0:
                # blank line
                continue
            elif "#include" in line:
                # import statement
                continue
            elif line.strip()[-1]==":":
                # section header
                continue
            elif m and current:
                # assembly instruction
                inst_address = "0x" + m.group(1)
                inst_bytes = m.group(2).strip()
                inst_assembly = m.group(4).strip()

                address = int(inst_address, 16)
                disassembly_ints = [int("0x"+s, 16) for s in inst_bytes.split()]
                disassembly_binary = []
                
                bits_fill = architectures_supported[target]["bits_fill"]
                disassembly_binary = [bin(int(i))[2:].zfill(bits_fill) for i in disassembly_ints]
                
                big_binary = "".join(disassembly_binary)
                length_bytes = len(big_binary)//8
                original = byte_array
                original_bytes = OriginalOverwrite(original, address + offset, length_bytes)

                current["instructions"].append({
                    "address": address,
                    "bytes": original_bytes,
                    "byte_code": inst_bytes,
                    "asm": inst_assembly
                })
            else:
                # actual c code
                result[line_number] = current
                line_number += 1
                current = {
                    "source": line.strip(),
                    "instructions": []
                }
        # last one
        result[line_number] = current
        f.close()
    return {file_name: result}

def main():
    ## entry point of this program
    ## Parsing the arguments
    parser = argparse.ArgumentParser(description="Tool Options")
    parser.add_argument("assembly", default="./m64.asm", type=str, help="Path to assembly.asm file")
    parser.add_argument("binary", default="./motivating.o", type=str, help="Path to binary.o")
    parser.add_argument("offset", default=40, type=int, help="Starting binary byte index")
    parser.add_argument("size", default=124, type=int, help="Size of .text section")
    parser.add_argument("out", default="./", type=str, help="Path to output folder")
    parser.add_argument("--t", default="x86_64", type=str, help="Target Architecture")
    
    args = parser.parse_args()
    assembly_path = args.assembly
    binary_path = args.binary
    offset = args.offset
    textsize = args.size
    out_path = args.out
    target = args.t

    file_name = os.path.basename(assembly_path)
    name = os.path.splitext(file_name)[0]
    
    out_file_path = os.path.join(out_path, f"{name}.json")

    byte_array = []
    try:
        with open(binary_path, "r+b") as f:
            mm = mmap.mmap(f.fileno(), 0)
            byte_array = bytearray(mm)
            sizefile=len(byte_array)
            print(f"{sizefile} bytes")
            f.close()
    except FileNotFoundError:
        print(f"Error: The file '{binary_path}' was not found.")

    data = parse_objdump(assembly_path, byte_array, offset, target)

    with open(out_file_path, "w") as f:
        f.write(json.dumps(data, indent=2))
        f.close()

    print(f"{out_file_path} created")

if __name__ == "__main__":
    main()
