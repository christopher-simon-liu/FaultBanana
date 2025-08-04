architectures_supported = {
    "i386": {
        "compile_command": "gcc -m32 -c -g -O0 -o {} {}",
        "link_command": "gcc -m32 -static -o {} {}",
        "disassemble_command": "objdump -d -S {} > {}",
        "parse_regex": r"([0-9a-fA-F]+):(\s+([0-9a-fA-F]{2}\s+)+)(.*)",
        "bits_fill": 8,
        "test_command": "qemu-i386 {}"
    },
}

