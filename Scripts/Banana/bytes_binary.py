# byte arrays and binary strings

def binary_to_byte_ints(binary_string):
    binary_list = list(binary_string)
    byte_int_list = []
    for i in range(0, len(binary_list), 8):
        byte_string = ""
        for j in range(8):
            index = i + j
            byte_string = byte_string + binary_list[index]
        byte_int_list.append(int(byte_string, 2))
    return byte_int_list

def byte_ints_to_binary(byte_int_list):
    binary_list = [bin(int(i))[2:].zfill(8) for i in byte_int_list]
    big_binary = "".join(binary_list)
    return big_binary
