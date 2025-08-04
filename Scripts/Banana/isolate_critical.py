
import json
from Banana.print_logger import logger

def find_index_impacted(sussy_index, instruction_indexes):
    length = len(instruction_indexes)
    i = 0
    j = 1
    while i < length -1:
        start_index = instruction_indexes[i]
        next_index = instruction_indexes[j]
        if (start_index <= sussy_index and sussy_index < next_index):
            return start_index
        i += 1
        j += 1
    return -1

def extract_sussy_array(quick_banana_json_path):
    sussy_indexes = []
    try:
        with open(quick_banana_json_path, 'r') as j:
            banana = json.load(j)
            sussy_indexes = [int(s, 16) for s in banana["sussy"]]
            j.close()
    except FileNotFoundError:
        logger.error(f"Error: The file '{quick_banana_json_path}' was not found.")
    except json.JSONDecodeError:
        logger.error(f"Error: Could not decode JSON from '{quick_banana_json_path}'. Check for valid JSON format.")
    return sussy_indexes

def extract_instructions_and_bytes(debug_json_path):
    instruction_data = {}
    try:
        with open(debug_json_path, 'r') as f:
            debug_json = json.load(f)
            for src_code_line in debug_json.keys():
                if debug_json[src_code_line]:
                    instructions = debug_json[src_code_line]["instructions"]
                    for instruction in instructions:
                        instruction_data[instruction["address"]] = instruction["bytes"]
            f.close()
    except FileNotFoundError:
        logger.error(f"Error: The file '{debug_json_path}' was not found.")
    except json.JSONDecodeError:
        logger.error(f"Error: Could not decode JSON from '{debug_json_path}'. Check for valid JSON format.")
    return instruction_data

# assume offsets are already included in index addresses
def isolate_critical(quick_banana_json_path, debug_json_path):
    critical_data = {}

    sussy_indexes = extract_sussy_array(quick_banana_json_path)
    
    instruction_data = extract_instructions_and_bytes(debug_json_path)
    instruction_indexes = [int(i, 16) for i in instruction_data.keys()]

    logger.info("Sussy Indexes")
    logger.info(sussy_indexes)

    logger.info("Starting Indexes of Instructions")
    logger.info(instruction_indexes)

    critical_instruction_set = set()
    for sussy_index in sussy_indexes:
        critical_index = find_index_impacted(sussy_index, instruction_indexes)
        if critical_index == -1: # not in instructtion indexes?
            continue
        critical_instruction_set.add(critical_index)
        logger.info(f"{sussy_index} byte fault impacts the instruction @ {critical_index}")

    for critical_index in critical_instruction_set:
        address = hex(critical_index)
        critical_data[address] = instruction_data[address]

    return critical_data

if __name__ == "__main__":
    main()
