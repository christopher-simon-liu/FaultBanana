
def rewriteByte(byte_array, out_file_path, position, mutant_byte_hex):
    store = open(out_file_path, 'wb')
    binary_to_mutate = byte_array.copy()
    binary_to_mutate[int(position)] = mutant_byte_hex
    store.write(binary_to_mutate)
    store.close()

def rewriteByteSection(byte_array, out_file_path, position, byte_list):
    store = open(out_file_path, 'wb')
    binary_to_mutate = byte_array.copy()
    size = len(byte_list)
    for i in range(size):
        index = int(position) + i
        binary_to_mutate[index] = byte_list[i]
    store.write(binary_to_mutate)
    store.close()
