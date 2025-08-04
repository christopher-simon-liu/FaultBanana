architectures = {
    "x86_64": {
        "compile_command": "gcc -m64 -c -g -O0 -o {} {}",
        "link_command": "gcc -m64 -static -o {} {}",
        "disassemble_command": "objdump -d -S {} > {}",
        "parse_regex": r"([0-9a-fA-F]+):(\s+([0-9a-fA-F]{2}\s+)+)(.*)",
        "test_command": "qemu-x86_64 {}"
    },
    "i386": {
        "compile_command": "gcc -m32 -c -g -O0 -o {} {}",
        "link_command": "gcc -m32 -static -o {} {}",
        "disassemble_command": "objdump -d -S {} > {}",
        "parse_regex": r"([0-9a-fA-F]+):(\s+([0-9a-fA-F]{2}\s+)+)(.*)",
        "test_command": "qemu-i386 {}"
    },
    "arm_32": {
        "compile_command": "arm-linux-gnueabihf-gcc -c -g -O0 -o {} {}",
        "link_command": "arm-linux-gnueabihf-gcc -static -o {} {}",
        "disassemble_command": "arm-linux-gnueabihf-objdump -d -S {} > {}",
        "parse_regex": r"([0-9a-fA-F]+):(\s+([0-9a-fA-F]{4}\s+)+)(.*)",
        "test_command": "qemu-arm {}"
    },
    "riscv32": {
        "compile_command": "~/Fault-Banana/riscv/bin/riscv32-unknown-elf-gcc -c -g -O0 -o {} {}",
        "link_command": "~/Fault-Banana/riscv/bin/riscv32-unknown-elf-gcc -static -o {} {}",
        "disassemble_command": "~/Fault-Banana/riscv/bin/riscv32-unknown-elf-objdump -d -S {} > {}",
        "parse_regex": r"([0-9a-fA-F]+):(\s+([0-9a-fA-F]{4}\s+)+|\s+([0-9a-fA-F]{8}\s+)+)(.*)",
        "test_command": "qemu-riscv32 {}"
    }

}
