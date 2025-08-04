import json
import subprocess
import re
from Banana.architecture_support import architectures
from Banana.print_logger import logger

def select_command(architecture, file_path, out_file_path):
    command_template = architectures[architecture]["disassemble_command"]
    return command_template.format(file_path, out_file_path)

def run_command(command):
    try:
        process = subprocess.run([command], check=True, capture_output=True, shell=True)
        logger.info(f"Disassembly completed with exit code: {process.returncode}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Disassembly failed with error: {e}")

def disassemble_binary(architecture, file_path, out_file_path):
    command = select_command(architecture, file_path, out_file_path)
    run_command(command)

def extract_snippet(byte_array, position, length_bytes):
    snippet = []
    for i in range(length_bytes):
        index = position + i
        snippet.append(byte_array[index])
    return snippet

def parse_disassembly(file_path, byte_array, offset, architecture):
    result = {}
    file_name = ""
    line_number = 0
    current = None

    regex_string = architectures[architecture]["parse_regex"]
    
    with open(file_path) as f:
        
        for line in f:
            # instruction info regex
            m = re.match(regex_string, line.strip())

            if "file format" in line:
                # binary name
                continue
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
                inst_machine_codes = m.group(2).strip()
                inst_assembly = m.groups()[-1].strip()

                # ff 2 char = 255 = 11111111 8 bits
                # ffff 4 char = 65535 = 1111111111111111 16 bits
                # ffffffff 8 char = 4294967295 = 11111111111111111111111111111111 32 bits
                bitsize = 0
                big_binary = ""
                for hex_code in inst_machine_codes.split():
                    if len(hex_code) == 2:
                        bitsize = 8
                    elif len(hex_code) == 4:
                        bitsize = 16
                    else: # hopefully 8
                        bitsize = 32
                    int_value = int("0x" + hex_code, 16)
                    binary_value = bin(int_value)[2:].zfill(bitsize)
                    big_binary = big_binary + binary_value

                length_bytes = len(big_binary) // 8
                
                position = int(inst_address, 16) + offset
                inst_bytes = extract_snippet(byte_array, position, length_bytes)

                # offset is added to addresses
                current["instructions"].append({
                    "address": hex(position),
                    "bytes": inst_bytes,
                    "code": inst_machine_codes,
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
    return result

