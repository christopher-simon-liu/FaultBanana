
def fault_set_byte_hex(byte_hex):
    return 0xFF

def fault_reset_byte_hex(byte_hex):
    return 0x00

def fault_flip_byte_hex(byte_hex):
    return byte_hex ^ 0xFF

def fault_set_byte_binary_string(offset, binary_string):
    binary_list = list(binary_string)
    for i in range(8):
        index = i + offset
        binary_list[index] = "1"
    
    return "".join(binary_list)

def fault_reset_byte_binary_string(offset, binary_string):
    binary_list = list(binary_string)
    for i in range(8):
        index = i + offset
        binary_list[index] = "0"
    
    return "".join(binary_list)

def fault_flip_byte_binary_string(offset, binary_string):
    binary_list = list(binary_string)
    for i in range(8):
        index = i + offset
        temp = binary_list[index]
        if temp == "0":
            binary_list[index] = "1"
        else:
            binary_list[index] = "0"
    
    return "".join(binary_list)

